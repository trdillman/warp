from __future__ import annotations

from pathlib import Path

import bpy

from sim_core.app import run_preset
from sim_core.contracts import SimulationRunRequest


class AstroSimRunPresetOperator(bpy.types.Operator):
    bl_idname = "astrosim.run_preset"
    bl_label = "Run Simulation Preset"
    bl_description = "Run the selected cinematic astrophysical simulation preset"

    def execute(self, context):
        settings = context.scene.astrosim_settings

        request = SimulationRunRequest(
            preset_id=settings.preset_id,
            steps=settings.steps,
            dt=settings.dt,
            output_dir=str(Path(settings.output_dir)),
            save_every=settings.save_every,
        )
        snapshots = run_preset(request)
        self.report({"INFO"}, f"Astro Sim wrote {len(snapshots)} snapshots")
        return {"FINISHED"}
