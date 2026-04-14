from __future__ import annotations

import math
import random

from sim_core.contracts import (
    SIMULATION_SPEC_VERSION,
    BackendRequirements,
    CacheSettings,
    MaterialDef,
    ParticleInit,
    PresetConfig,
    PresetMeta,
    PresetPlugin,
    RuntimeSettings,
    SimulationSpec,
    VisualizationHints,
)


class MoonBirthTheiaPreset(PresetPlugin):
    """Preset for cinematic Theia impact style simulations."""

    meta = PresetMeta(
        preset_id="moon_birth_theia",
        display_name="Moon Birth / Theia Impact",
        description="Simplified two-body particle cloud impact for VFX previs.",
        tags=("planetary", "impact", "moon-formation"),
        category="astro_impact",
    )

    def default_config(self) -> PresetConfig:
        return PresetConfig(
            values={
                "earth_particles": 128,
                "theia_particles": 96,
                "earth_radius": 3.0,
                "theia_radius": 2.0,
                "theia_offset": [7.0, 0.0, 0.0],
                "theia_velocity": [-0.25, 0.15, 0.0],
                "gravity_mu": 1.5,
                "seed": 7,
                "dt": 0.05,
                "default_steps": 24,
                "save_every": 3,
                "point_radius": 0.18,
            }
        )

    def compile_spec(self, config: PresetConfig) -> SimulationSpec:
        values = config.values
        rng = random.Random(values["seed"])

        positions: list[list[float]] = []
        velocities: list[list[float]] = []
        masses: list[float] = []
        materials: list[str] = []

        self._emit_body(
            count=int(values["earth_particles"]),
            radius=float(values["earth_radius"]),
            center=[0.0, 0.0, 0.0],
            velocity=[0.0, 0.0, 0.0],
            mass=1.0,
            material="earth_mantle",
            rng=rng,
            positions=positions,
            velocities=velocities,
            masses=masses,
            materials=materials,
        )
        self._emit_body(
            count=int(values["theia_particles"]),
            radius=float(values["theia_radius"]),
            center=list(values["theia_offset"]),
            velocity=list(values["theia_velocity"]),
            mass=0.6,
            material="theia_mantle",
            rng=rng,
            positions=positions,
            velocities=velocities,
            masses=masses,
            materials=materials,
        )

        return SimulationSpec(
            spec_version=SIMULATION_SPEC_VERSION,
            preset_id=self.meta.preset_id,
            particle_init=ParticleInit(positions=positions, velocities=velocities, masses=masses, materials=materials),
            materials=[
                MaterialDef(material_id="earth_mantle", display_name="Earth Mantle"),
                MaterialDef(material_id="theia_mantle", display_name="Theia Mantle"),
            ],
            solver_config={"gravity_model": "central", "gravity_mu": float(values["gravity_mu"])},
            runtime=RuntimeSettings(dt=float(values["dt"]), default_steps=int(values["default_steps"])),
            backend_requirements=BackendRequirements(backend="warp", features=("particles", "gravity")),
            cache_settings=CacheSettings(
                save_every=int(values["save_every"]), cache_format="json", include_velocity=True
            ),
            visualization_hints=VisualizationHints(point_radius=float(values["point_radius"]), color_mode="material"),
            parameter_defaults=dict(values),
        )

    @staticmethod
    def _emit_body(
        *,
        count: int,
        radius: float,
        center: list[float],
        velocity: list[float],
        mass: float,
        material: str,
        rng: random.Random,
        positions: list[list[float]],
        velocities: list[list[float]],
        masses: list[float],
        materials: list[str],
    ) -> None:
        for _ in range(count):
            u = rng.random()
            v = rng.random()
            w = rng.random()

            theta = 2.0 * math.pi * u
            phi = math.acos(2.0 * v - 1.0)
            r = radius * (w ** (1.0 / 3.0))

            x = r * math.sin(phi) * math.cos(theta)
            y = r * math.sin(phi) * math.sin(theta)
            z = r * math.cos(phi)

            positions.append([center[0] + x, center[1] + y, center[2] + z])
            velocities.append([velocity[0], velocity[1], velocity[2]])
            masses.append(mass)
            materials.append(material)
