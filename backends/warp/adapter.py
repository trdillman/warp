from __future__ import annotations

from dataclasses import dataclass

import numpy as np

import warp as wp
from sim_core.contracts import CACHE_SCHEMA_VERSION, SimulationSpec, SimulationState


@wp.kernel
def apply_central_gravity(
    positions: wp.array(dtype=wp.vec3),
    velocities: wp.array(dtype=wp.vec3),
    masses: wp.array(dtype=float),
    dt: float,
    gravity_mu: float,
):
    tid = wp.tid()
    p = positions[tid]
    v = velocities[tid]

    r2 = wp.max(wp.dot(p, p), 1.0e-6)
    inv_r = 1.0 / wp.sqrt(r2)
    inv_r3 = inv_r * inv_r * inv_r

    accel = -gravity_mu * inv_r3 * p
    v = v + accel * dt
    p = p + v * dt

    velocities[tid] = v
    positions[tid] = p


@dataclass
class WarpRuntimeState:
    positions: wp.array
    velocities: wp.array
    masses: wp.array
    materials: list[str]


class WarpBackendAdapter:
    """Warp backend adapter for the shared runtime contract."""

    name = "warp"

    def __init__(self, device: str | None = None):
        self.device = device
        self.gravity_mu = 1.0
        wp.init()

    def initialize(self, spec: SimulationSpec) -> WarpRuntimeState:
        pos_np = np.asarray(spec.particle_init.positions, dtype=np.float32)
        vel_np = np.asarray(spec.particle_init.velocities, dtype=np.float32)
        masses_np = np.asarray(spec.particle_init.masses, dtype=np.float32)
        self.gravity_mu = float(spec.solver_config.get("gravity_mu", 1.0))

        return WarpRuntimeState(
            positions=wp.array(pos_np, dtype=wp.vec3, device=self.device),
            velocities=wp.array(vel_np, dtype=wp.vec3, device=self.device),
            masses=wp.array(masses_np, dtype=float, device=self.device),
            materials=list(spec.particle_init.materials),
        )

    def step(self, runtime_state: WarpRuntimeState, dt: float) -> None:
        wp.launch(
            kernel=apply_central_gravity,
            dim=runtime_state.positions.shape[0],
            inputs=[runtime_state.positions, runtime_state.velocities, runtime_state.masses, dt, self.gravity_mu],
            device=runtime_state.positions.device,
        )

    def snapshot(self, runtime_state: WarpRuntimeState, frame: int, time: float) -> SimulationState:
        return SimulationState(
            schema_version=CACHE_SCHEMA_VERSION,
            frame=frame,
            time=time,
            positions=runtime_state.positions.numpy().tolist(),
            velocities=runtime_state.velocities.numpy().tolist(),
            masses=runtime_state.masses.numpy().tolist(),
            materials=list(runtime_state.materials),
        )
