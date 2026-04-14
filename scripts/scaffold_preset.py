from __future__ import annotations

import argparse
from pathlib import Path

TEMPLATE = """from __future__ import annotations

from sim_core.contracts import (
    BackendRequirements,
    CacheSettings,
    MaterialDef,
    ParticleInit,
    PresetConfig,
    PresetMeta,
    PresetPlugin,
    RuntimeSettings,
    SIMULATION_SPEC_VERSION,
    SimulationSpec,
    VisualizationHints,
)


class {class_name}(PresetPlugin):
    meta = PresetMeta(
        preset_id="{preset_id}",
        display_name="{display_name}",
        description="TODO: describe preset",
        tags=("todo",),
        category="astro",
    )

    def default_config(self) -> PresetConfig:
        return PresetConfig(values={{"particle_count": 64, "dt": 0.05, "default_steps": 20, "save_every": 2}})

    def compile_spec(self, config: PresetConfig) -> SimulationSpec:
        values = config.values
        count = int(values["particle_count"])
        positions = [[0.0, 0.0, 0.0] for _ in range(count)]
        velocities = [[0.0, 0.0, 0.0] for _ in range(count)]
        masses = [1.0 for _ in range(count)]
        materials = ["default" for _ in range(count)]

        return SimulationSpec(
            spec_version=SIMULATION_SPEC_VERSION,
            preset_id=self.meta.preset_id,
            particle_init=ParticleInit(positions=positions, velocities=velocities, masses=masses, materials=materials),
            materials=[MaterialDef(material_id="default", display_name="Default")],
            solver_config={{"gravity_model": "central", "gravity_mu": 1.0}},
            runtime=RuntimeSettings(dt=float(values["dt"]), default_steps=int(values["default_steps"])),
            backend_requirements=BackendRequirements(backend="warp", features=("particles",)),
            cache_settings=CacheSettings(save_every=int(values["save_every"])),
            visualization_hints=VisualizationHints(point_radius=0.1, color_mode="material"),
            parameter_defaults=dict(values),
        )
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Scaffold a new preset module from template")
    parser.add_argument("preset_id", help="snake_case preset ID")
    args = parser.parse_args()

    preset_id = args.preset_id
    class_name = "".join(part.capitalize() for part in preset_id.split("_")) + "Preset"
    display_name = preset_id.replace("_", " ").title()
    path = Path("presets") / f"{preset_id}.py"
    if path.exists():
        raise FileExistsError(f"Preset file already exists: {path}")

    path.write_text(
        TEMPLATE.format(class_name=class_name, preset_id=preset_id, display_name=display_name),
        encoding="utf-8",
    )
    print(f"Created preset template: {path}")


if __name__ == "__main__":
    main()
