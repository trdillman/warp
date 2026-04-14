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
    ProvenanceDef,
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
                "base_h": 0.25,
                "dt": 0.04,
                "default_steps": 30,
                "dt_min": 0.01,
                "dt_max": 0.05,
                "cfl_factor": 0.35,
                "accel_factor": 0.25,
                "displacement_factor": 0.2,
                "save_every": 3,
                "diagnostics_every": 1,
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
        material_ids: list[int] = []
        provenance_ids: list[int] = []
        smoothing_lengths: list[float] = []
        internal_energy: list[float] = []

        for _ in range(count):
            theta = rng.uniform(0.0, 2.0 * math.pi)
            radius = rng.uniform(r_min, r_max) + rng.uniform(-jitter, jitter)
            z = rng.uniform(-0.4, 0.4)

            x = radius * math.cos(theta)
            y = radius * math.sin(theta)
            tangent = [-math.sin(theta), math.cos(theta), 0.0]

            positions.append([x, y, z])
            velocities.append([tangent[0] * speed, tangent[1] * speed, 0.0])
            masses.append(0.08)
            material_ids.append(0)
            provenance_ids.append(0)
            smoothing_lengths.append(float(values["base_h"]))
            internal_energy.append(0.4)

        return SimulationSpec(
            spec_version=SIMULATION_SPEC_VERSION,
            preset_id=self.meta.preset_id,
            body_configs=[],
            particle_init=ParticleInit(
                positions=positions,
                velocities=velocities,
                masses=masses,
                material_ids=material_ids,
                provenance_ids=provenance_ids,
                smoothing_lengths=smoothing_lengths,
                internal_energy=internal_energy,
            ),
            materials=[
                MaterialDef(material_id=0, name="asteroid_rock", eos_model="tait", eos_params={"k": 6.0, "gamma": 6.0})
            ],
            provenances=[ProvenanceDef(provenance_id=0, name="asteroid_belt")],
            eos_config={"model": "analytic_tait", "table_ready": True},
            solver_config={
                "mode": "giant_impact_sph",
                "gravity_model": "all_pairs_softened",
                "gravity_softening": 0.12,
                "sph_stiffness": 6.0,
                "artificial_viscosity": 0.8,
            },
            runtime=RuntimeSettings(
                dt=float(values["dt"]),
                default_steps=int(values["default_steps"]),
                dt_min=float(values["dt_min"]),
                dt_max=float(values["dt_max"]),
                cfl_factor=float(values["cfl_factor"]),
                accel_factor=float(values["accel_factor"]),
                displacement_factor=float(values["displacement_factor"]),
            ),
            backend_requirements=BackendRequirements(backend="warp", features=("sph_density", "self_gravity")),
            cache_settings=CacheSettings(
                save_every=int(values["save_every"]),
                cache_format="json",
                include_velocity=True,
                diagnostics_every=int(values["diagnostics_every"]),
            ),
            visualization_hints=VisualizationHints(point_radius=float(values["point_radius"]), color_mode="material"),
            diagnostics_config={"roche_limit": 2.5, "central_radius_estimate": 1.0},
            settle_config={"steps": 0, "damping": 1.0, "cache": False},
            parameter_defaults=dict(values),
        )
