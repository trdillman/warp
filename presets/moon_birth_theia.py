from __future__ import annotations

import math
import random

from sim_core.contracts import (
    SIMULATION_SPEC_VERSION,
    BackendRequirements,
    BodyInitConfig,
    CacheSettings,
    MaterialDef,
    PresetConfig,
    PresetMeta,
    PresetPlugin,
    ProvenanceDef,
    RuntimeSettings,
    SimulationSpec,
    VisualizationHints,
)
from sim_core.initial_conditions import build_differentiated_body_particles, merge_particle_inits


class MoonBirthTheiaPreset(PresetPlugin):
    """Cinematic giant-impact setup with differentiated proto-Earth and Theia bodies."""

    meta = PresetMeta(
        preset_id="moon_birth_theia",
        display_name="Moon Birth / Theia Impact",
        description="Differentiated grazing impact with SPH + self-gravity for early disk-like debris formation.",
        tags=("giant-impact", "moon-birth", "sph", "vfx"),
        category="astro_impact",
    )

    def default_config(self) -> PresetConfig:
        return PresetConfig(
            values={
                "seed": 17,
                "earth_particles": 160,
                "theia_particles": 96,
                "earth_radius": 1.0,
                "theia_radius": 0.56,
                "earth_core_fraction": 0.28,
                "theia_core_fraction": 0.24,
                "impact_angle_deg": 44.0,
                "impact_speed_escape_multiple": 1.05,
                "earth_spin_z": 0.08,
                "theia_spin_z": -0.03,
                "base_smoothing_length": 0.16,
                "gravity_softening": 0.08,
                "sph_stiffness": 12.0,
                "artificial_viscosity": 1.2,
                "density0_mantle": 1.0,
                "density0_core": 1.8,
                "settle_steps": 18,
                "settle_damping": 0.94,
                "dt": 0.01,
                "default_steps": 220,
                "dt_min": 0.001,
                "dt_max": 0.02,
                "cfl_factor": 0.35,
                "accel_factor": 0.25,
                "displacement_factor": 0.2,
                "save_every": 5,
                "diagnostics_every": 1,
                "roche_limit": 2.5,
                "point_radius": 0.045,
            }
        )

    def compile_spec(self, config: PresetConfig) -> SimulationSpec:
        v = config.values
        rng = random.Random(v["seed"])

        earth = BodyInitConfig(
            body_id="earth",
            particle_count=int(v["earth_particles"]),
            radius=float(v["earth_radius"]),
            core_fraction=float(v["earth_core_fraction"]),
            core_density=float(v["density0_core"]),
            mantle_density=float(v["density0_mantle"]),
            position=[0.0, 0.0, 0.0],
            velocity=[0.0, 0.0, 0.0],
            spin=[0.0, 0.0, float(v["earth_spin_z"])],
            core_material_id=1,
            mantle_material_id=0,
            core_provenance_id=1,
            mantle_provenance_id=0,
        )

        impact_angle = math.radians(float(v["impact_angle_deg"]))
        separation = earth.radius + float(v["theia_radius"]) * 1.2
        impact_pos = [separation * math.cos(impact_angle), separation * math.sin(impact_angle), 0.0]
        v_escape = math.sqrt(2.0 * (earth.radius + float(v["theia_radius"])))
        impact_speed = float(v["impact_speed_escape_multiple"]) * v_escape

        theia = BodyInitConfig(
            body_id="theia",
            particle_count=int(v["theia_particles"]),
            radius=float(v["theia_radius"]),
            core_fraction=float(v["theia_core_fraction"]),
            core_density=float(v["density0_core"]),
            mantle_density=float(v["density0_mantle"]),
            position=impact_pos,
            velocity=[-impact_speed * math.cos(impact_angle), -impact_speed * math.sin(impact_angle), 0.0],
            spin=[0.0, 0.0, float(v["theia_spin_z"])],
            core_material_id=1,
            mantle_material_id=0,
            core_provenance_id=3,
            mantle_provenance_id=2,
        )

        particle_init = merge_particle_inits(
            [
                build_differentiated_body_particles(earth, rng, base_h=float(v["base_smoothing_length"])),
                build_differentiated_body_particles(theia, rng, base_h=float(v["base_smoothing_length"])),
            ]
        )

        return SimulationSpec(
            spec_version=SIMULATION_SPEC_VERSION,
            preset_id=self.meta.preset_id,
            body_configs=[earth, theia],
            particle_init=particle_init,
            materials=[
                MaterialDef(material_id=0, name="silicate", eos_model="tait", eos_params={"k": 12.0, "gamma": 7.0}),
                MaterialDef(material_id=1, name="iron", eos_model="tait", eos_params={"k": 18.0, "gamma": 7.5}),
            ],
            provenances=[
                ProvenanceDef(provenance_id=0, name="earth_mantle"),
                ProvenanceDef(provenance_id=1, name="earth_core"),
                ProvenanceDef(provenance_id=2, name="theia_mantle"),
                ProvenanceDef(provenance_id=3, name="theia_core"),
            ],
            eos_config={"model": "analytic_tait", "table_ready": True},
            solver_config={
                "mode": "giant_impact_sph",
                "gravity_model": "all_pairs_softened",
                "gravity_softening": float(v["gravity_softening"]),
                "sph_stiffness": float(v["sph_stiffness"]),
                "artificial_viscosity": float(v["artificial_viscosity"]),
            },
            runtime=RuntimeSettings(
                dt=float(v["dt"]),
                default_steps=int(v["default_steps"]),
                dt_min=float(v["dt_min"]),
                dt_max=float(v["dt_max"]),
                cfl_factor=float(v["cfl_factor"]),
                accel_factor=float(v["accel_factor"]),
                displacement_factor=float(v["displacement_factor"]),
            ),
            backend_requirements=BackendRequirements(
                backend="warp",
                features=("sph_density", "pressure", "self_gravity", "neighbor_search", "adaptive_dt"),
            ),
            cache_settings=CacheSettings(
                save_every=int(v["save_every"]),
                cache_format="json",
                include_velocity=True,
                diagnostics_every=int(v["diagnostics_every"]),
            ),
            visualization_hints=VisualizationHints(point_radius=float(v["point_radius"]), color_mode="provenance"),
            diagnostics_config={"roche_limit": float(v["roche_limit"]), "central_radius_estimate": 1.2},
            settle_config={"steps": int(v["settle_steps"]), "damping": float(v["settle_damping"]), "cache": True},
            parameter_defaults=dict(v),
        )
