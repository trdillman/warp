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


class AsteroidBeltDisruptionPreset(PresetPlugin):
    """Preset for cinematic asteroid belt disruption sequences."""

    meta = PresetMeta(
        preset_id="asteroid_belt_disruption",
        display_name="Asteroid Belt Disruption",
        description="Ring-distributed particles with tangential drift and perturbation.",
        tags=("asteroid", "belt", "disruption"),
        category="astro_orbital",
    )

    def default_config(self) -> PresetConfig:
        return PresetConfig(
            values={
                "particle_count": 220,
                "inner_radius": 7.0,
                "outer_radius": 12.0,
                "orbital_speed": 0.35,
                "radial_jitter": 0.6,
                "seed": 11,
                "gravity_mu": 0.9,
                "dt": 0.04,
                "default_steps": 30,
                "save_every": 3,
                "point_radius": 0.1,
            }
        )

    def compile_spec(self, config: PresetConfig) -> SimulationSpec:
        values = config.values
        rng = random.Random(values["seed"])

        count = int(values["particle_count"])
        r_min = float(values["inner_radius"])
        r_max = float(values["outer_radius"])
        speed = float(values["orbital_speed"])
        jitter = float(values["radial_jitter"])

        positions: list[list[float]] = []
        velocities: list[list[float]] = []
        masses: list[float] = []
        materials: list[str] = []

        for _ in range(count):
            theta = rng.uniform(0.0, 2.0 * math.pi)
            radius = rng.uniform(r_min, r_max)
            radius += rng.uniform(-jitter, jitter)
            z = rng.uniform(-0.4, 0.4)

            x = radius * math.cos(theta)
            y = radius * math.sin(theta)

            tangent = [-math.sin(theta), math.cos(theta), 0.0]
            vx = tangent[0] * speed
            vy = tangent[1] * speed

            positions.append([x, y, z])
            velocities.append([vx, vy, 0.0])
            masses.append(0.08)
            materials.append("asteroid_rock")

        return SimulationSpec(
            spec_version=SIMULATION_SPEC_VERSION,
            preset_id=self.meta.preset_id,
            particle_init=ParticleInit(positions=positions, velocities=velocities, masses=masses, materials=materials),
            materials=[MaterialDef(material_id="asteroid_rock", display_name="Asteroid Rock")],
            solver_config={"gravity_model": "central", "gravity_mu": float(values["gravity_mu"])},
            runtime=RuntimeSettings(dt=float(values["dt"]), default_steps=int(values["default_steps"])),
            backend_requirements=BackendRequirements(backend="warp", features=("particles", "gravity")),
            cache_settings=CacheSettings(
                save_every=int(values["save_every"]), cache_format="json", include_velocity=True
            ),
            visualization_hints=VisualizationHints(point_radius=float(values["point_radius"]), color_mode="material"),
            parameter_defaults=dict(values),
        )
