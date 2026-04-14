from __future__ import annotations

from dataclasses import dataclass

import numpy as np

import warp as wp
from sim_core.contracts import CACHE_SCHEMA_VERSION, SimulationSpec, SimulationState


@wp.func
def poly6_kernel(r: float, h: float) -> float:
    if r >= h:
        return 0.0
    x = h * h - r * r
    return x * x * x


@wp.func
def spiky_grad_scale(r: float, h: float) -> float:
    if r <= 1.0e-6 or r >= h:
        return 0.0
    x = h - r
    return x * x / r


@wp.kernel
def compute_density_pressure(
    grid: wp.uint64,
    count: int,
    positions: wp.array(dtype=wp.vec3),
    smoothing_lengths: wp.array(dtype=float),
    masses: wp.array(dtype=float),
    rest_density: wp.array(dtype=float),
    stiffness: float,
    densities: wp.array(dtype=float),
    pressures: wp.array(dtype=float),
):
    i = wp.tid()
    if i >= count:
        return

    p_i = positions[i]
    h_i = smoothing_lengths[i]
    rho = float(0.0)

    neighbors = wp.hash_grid_query(grid, p_i, h_i)
    for j in neighbors:
        r = wp.length(p_i - positions[j])
        rho += masses[j] * poly6_kernel(r, h_i)

    rho = wp.max(rho, 1.0e-5)
    densities[i] = rho
    pressures[i] = stiffness * (rho - rest_density[i])


@wp.kernel
def compute_accel_energy(
    grid: wp.uint64,
    count: int,
    positions: wp.array(dtype=wp.vec3),
    velocities: wp.array(dtype=wp.vec3),
    masses: wp.array(dtype=float),
    smoothing_lengths: wp.array(dtype=float),
    densities: wp.array(dtype=float),
    pressures: wp.array(dtype=float),
    artificial_viscosity: float,
    gravity_softening: float,
    accel: wp.array(dtype=wp.vec3),
    du_dt: wp.array(dtype=float),
):
    i = wp.tid()
    if i >= count:
        return

    p_i = positions[i]
    v_i = velocities[i]
    h_i = smoothing_lengths[i]
    rho_i = densities[i]
    p_i_pressure = pressures[i]

    a = wp.vec3()
    du = float(0.0)

    neighbors = wp.hash_grid_query(grid, p_i, h_i)
    for j in neighbors:
        if j == i:
            continue

        p_j = positions[j]
        v_j = velocities[j]
        rho_j = wp.max(densities[j], 1.0e-5)
        p_j_pressure = pressures[j]

        r_vec = p_i - p_j
        r = wp.length(r_vec)
        grad_scale = spiky_grad_scale(r, h_i)

        pressure_term = -masses[j] * (p_i_pressure / (rho_i * rho_i) + p_j_pressure / (rho_j * rho_j)) * grad_scale
        a += pressure_term * r_vec

        v_rel = v_i - v_j
        visc = artificial_viscosity * masses[j] * wp.dot(v_rel, r_vec) / (rho_j * (r * r + 0.01 * h_i * h_i))
        a += -visc * r_vec
        du += visc * wp.length(v_rel)

    for j in range(count):
        if j == i:
            continue
        r_vec = positions[j] - p_i
        r2 = wp.dot(r_vec, r_vec) + gravity_softening * gravity_softening
        inv_r = 1.0 / wp.sqrt(r2)
        inv_r3 = inv_r * inv_r * inv_r
        a += masses[j] * r_vec * inv_r3

    accel[i] = a
    du_dt[i] = du


@wp.kernel
def integrate_state(
    count: int,
    dt: float,
    positions: wp.array(dtype=wp.vec3),
    velocities: wp.array(dtype=wp.vec3),
    internal_energy: wp.array(dtype=float),
    accel: wp.array(dtype=wp.vec3),
    du_dt: wp.array(dtype=float),
):
    i = wp.tid()
    if i >= count:
        return

    v = velocities[i] + accel[i] * dt
    x = positions[i] + v * dt

    velocities[i] = v
    positions[i] = x
    internal_energy[i] = wp.max(internal_energy[i] + du_dt[i] * dt, 0.0)


@wp.kernel
def damp_velocities(count: int, damping: float, velocities: wp.array(dtype=wp.vec3)):
    i = wp.tid()
    if i >= count:
        return
    velocities[i] = velocities[i] * damping


@dataclass
class WarpRuntimeState:
    positions: wp.array
    velocities: wp.array
    masses: wp.array
    material_ids: wp.array
    provenance_ids: wp.array
    smoothing_lengths: wp.array
    internal_energy: wp.array
    rest_density: wp.array
    densities: wp.array
    pressures: wp.array
    accel: wp.array
    du_dt: wp.array
    grid: wp.HashGrid
    count: int
    last_step_stats: dict[str, float]


class WarpBackendAdapter:
    """Warp backend adapter with SPH + softened self-gravity for VFX giant-impact shots."""

    name = "warp"

    def __init__(self, device: str | None = None):
        self.device = device
        self.stiffness = 10.0
        self.artificial_viscosity = 1.0
        self.gravity_softening = 0.08
        wp.init()

    def _build_rest_density(self, spec: SimulationSpec) -> np.ndarray:
        lookup: dict[int, float] = {}
        for mat in spec.materials:
            lookup[mat.material_id] = float(mat.eos_params.get("rho0", 1.0))
        return np.asarray([lookup.get(mid, 1.0) for mid in spec.particle_init.material_ids], dtype=np.float32)

    def initialize(self, spec: SimulationSpec) -> WarpRuntimeState:
        self.stiffness = float(spec.solver_config.get("sph_stiffness", 10.0))
        self.artificial_viscosity = float(spec.solver_config.get("artificial_viscosity", 1.0))
        self.gravity_softening = float(spec.solver_config.get("gravity_softening", 0.08))

        pos_np = np.asarray(spec.particle_init.positions, dtype=np.float32)
        vel_np = np.asarray(spec.particle_init.velocities, dtype=np.float32)
        masses_np = np.asarray(spec.particle_init.masses, dtype=np.float32)
        material_ids_np = np.asarray(spec.particle_init.material_ids, dtype=np.int32)
        provenance_ids_np = np.asarray(spec.particle_init.provenance_ids, dtype=np.int32)
        h_np = np.asarray(spec.particle_init.smoothing_lengths, dtype=np.float32)
        u_np = np.asarray(spec.particle_init.internal_energy, dtype=np.float32)
        rest_density_np = self._build_rest_density(spec)

        count = len(pos_np)
        grid_dim = max(32, int(np.cbrt(max(1, count)) * 8))
        grid = wp.HashGrid(grid_dim, grid_dim, grid_dim, device=self.device)

        return WarpRuntimeState(
            positions=wp.array(pos_np, dtype=wp.vec3, device=self.device),
            velocities=wp.array(vel_np, dtype=wp.vec3, device=self.device),
            masses=wp.array(masses_np, dtype=float, device=self.device),
            material_ids=wp.array(material_ids_np, dtype=int, device=self.device),
            provenance_ids=wp.array(provenance_ids_np, dtype=int, device=self.device),
            smoothing_lengths=wp.array(h_np, dtype=float, device=self.device),
            internal_energy=wp.array(u_np, dtype=float, device=self.device),
            rest_density=wp.array(rest_density_np, dtype=float, device=self.device),
            densities=wp.zeros(count, dtype=float, device=self.device),
            pressures=wp.zeros(count, dtype=float, device=self.device),
            accel=wp.zeros(count, dtype=wp.vec3, device=self.device),
            du_dt=wp.zeros(count, dtype=float, device=self.device),
            grid=grid,
            count=count,
            last_step_stats={},
        )

    def initialize_from_state(self, spec: SimulationSpec, state: SimulationState) -> WarpRuntimeState:
        runtime = self.initialize(spec)
        wp.copy(
            runtime.positions,
            wp.array(np.asarray(state.positions, dtype=np.float32), dtype=wp.vec3, device=self.device),
        )
        wp.copy(
            runtime.velocities,
            wp.array(np.asarray(state.velocities, dtype=np.float32), dtype=wp.vec3, device=self.device),
        )
        wp.copy(
            runtime.densities, wp.array(np.asarray(state.densities, dtype=np.float32), dtype=float, device=self.device)
        )
        wp.copy(
            runtime.internal_energy,
            wp.array(np.asarray(state.internal_energy, dtype=np.float32), dtype=float, device=self.device),
        )
        wp.copy(
            runtime.smoothing_lengths,
            wp.array(np.asarray(state.smoothing_lengths, dtype=np.float32), dtype=float, device=self.device),
        )
        return runtime

    def settle(self, runtime_state: WarpRuntimeState, spec: SimulationSpec) -> None:
        settle_steps = int(spec.settle_config.get("steps", 0))
        damping = float(spec.settle_config.get("damping", 1.0))
        if settle_steps <= 0:
            return
        settle_dt = min(spec.runtime.dt, 0.005)
        for _ in range(settle_steps):
            self.step(runtime_state, settle_dt)
            wp.launch(
                damp_velocities,
                dim=runtime_state.count,
                inputs=[runtime_state.count, damping, runtime_state.velocities],
            )

    def _build_grid(self, runtime_state: WarpRuntimeState) -> None:
        h_mean = float(np.mean(runtime_state.smoothing_lengths.numpy()))
        runtime_state.grid.build(points=runtime_state.positions, radius=max(h_mean, 1.0e-4))

    def step(self, runtime_state: WarpRuntimeState, dt: float) -> dict[str, float]:
        self._build_grid(runtime_state)

        wp.launch(
            compute_density_pressure,
            dim=runtime_state.count,
            inputs=[
                runtime_state.grid.id,
                runtime_state.count,
                runtime_state.positions,
                runtime_state.smoothing_lengths,
                runtime_state.masses,
                runtime_state.rest_density,
                self.stiffness,
                runtime_state.densities,
                runtime_state.pressures,
            ],
        )

        wp.launch(
            compute_accel_energy,
            dim=runtime_state.count,
            inputs=[
                runtime_state.grid.id,
                runtime_state.count,
                runtime_state.positions,
                runtime_state.velocities,
                runtime_state.masses,
                runtime_state.smoothing_lengths,
                runtime_state.densities,
                runtime_state.pressures,
                self.artificial_viscosity,
                self.gravity_softening,
                runtime_state.accel,
                runtime_state.du_dt,
            ],
        )

        wp.launch(
            integrate_state,
            dim=runtime_state.count,
            inputs=[
                runtime_state.count,
                dt,
                runtime_state.positions,
                runtime_state.velocities,
                runtime_state.internal_energy,
                runtime_state.accel,
                runtime_state.du_dt,
            ],
        )

        vel = runtime_state.velocities.numpy()
        acc = runtime_state.accel.numpy()
        h = runtime_state.smoothing_lengths.numpy()

        if not np.all(np.isfinite(vel)):
            vel = np.nan_to_num(vel, nan=0.0, posinf=0.0, neginf=0.0)
            runtime_state.velocities = wp.array(vel.astype(np.float32), dtype=wp.vec3, device=self.device)

        if not np.all(np.isfinite(acc)):
            acc = np.nan_to_num(acc, nan=0.0, posinf=0.0, neginf=0.0)

        speed = np.linalg.norm(vel, axis=1)
        accel_norm = np.linalg.norm(acc, axis=1)
        max_speed = float(np.max(speed))
        max_accel = float(np.max(accel_norm))
        min_h = float(np.min(h))

        runtime_state.last_step_stats = {
            "max_speed": max_speed,
            "max_accel": max_accel,
            "min_h": min_h,
            "cfl_dt": float(min_h / max(1.0e-6, max_speed)),
            "accel_dt": float(np.sqrt(min_h / max(1.0e-6, max_accel))),
            "disp_dt": float(0.5 * min_h / max(1.0e-6, max_speed)),
        }
        return runtime_state.last_step_stats

    def snapshot(self, runtime_state: WarpRuntimeState, frame: int, time: float) -> SimulationState:
        return SimulationState(
            schema_version=CACHE_SCHEMA_VERSION,
            frame=frame,
            time=time,
            positions=runtime_state.positions.numpy().tolist(),
            velocities=runtime_state.velocities.numpy().tolist(),
            masses=runtime_state.masses.numpy().tolist(),
            densities=runtime_state.densities.numpy().tolist(),
            internal_energy=runtime_state.internal_energy.numpy().tolist(),
            smoothing_lengths=runtime_state.smoothing_lengths.numpy().tolist(),
            material_ids=runtime_state.material_ids.numpy().tolist(),
            provenance_ids=runtime_state.provenance_ids.numpy().tolist(),
        )
