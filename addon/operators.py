from __future__ import annotations

from pathlib import Path

import bpy

from sim_core.app import create_runtime
from sim_core.contracts import PresetConfig, SimulationRunRequest

from .cache_bridge import build_preview_config, find_latest_snapshot, load_display_payload
from .visualization import update_preview_object


class AstroSimRunPresetOperator(bpy.types.Operator):
    bl_idname = "astrosim.run_preset"
    bl_label = "Run Simulation"
    bl_description = "Run the selected cinematic astrophysical simulation preset"

    def execute(self, context):
        settings = context.scene.astrosim_settings
        runtime = create_runtime("warp")

        config: PresetConfig | None = None
        if settings.use_preview:
            plugin = runtime.registry.get(settings.preset_id)
            config = build_preview_config(plugin.default_config(), settings.preview_steps, settings.preview_save_every)

        request = SimulationRunRequest(
            preset_id=settings.preset_id,
            steps=settings.steps if not settings.use_preview else settings.preview_steps,
            dt=settings.dt,
            output_dir=str(Path(settings.output_dir)),
            save_every=settings.save_every if not settings.use_preview else settings.preview_save_every,
        )
        snapshots = runtime.run(request, config=config)
        if not snapshots:
            self.report({"WARNING"}, "Run completed but no snapshots were produced.")
            return {"CANCELLED"}

        latest = Path(snapshots[-1])
        settings.active_snapshot_path = str(latest)
        settings.active_cache_dir = str(latest.parent)
        payload = load_display_payload(latest, settings.display_mode)
        obj = update_preview_object(payload)
        self.report({"INFO"}, f"Loaded frame {payload.frame} into object '{obj.name}'")
        return {"FINISHED"}


class AstroSimLoadLatestSnapshotOperator(bpy.types.Operator):
    bl_idname = "astrosim.load_latest_snapshot"
    bl_label = "Load Latest Snapshot"
    bl_description = "Load the latest cache snapshot into the viewport"

    def execute(self, context):
        settings = context.scene.astrosim_settings
        cache_dir = Path(settings.active_cache_dir or Path(settings.output_dir) / "cache")

        try:
            snapshot = find_latest_snapshot(cache_dir)
            payload = load_display_payload(snapshot, settings.display_mode)
            update_preview_object(payload)
        except FileNotFoundError as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}

        settings.active_snapshot_path = str(snapshot)
        settings.active_cache_dir = str(snapshot.parent)
        self.report({"INFO"}, f"Loaded latest snapshot frame {payload.frame}")
        return {"FINISHED"}


class AstroSimRefreshDisplayOperator(bpy.types.Operator):
    bl_idname = "astrosim.refresh_display"
    bl_label = "Refresh Display"
    bl_description = "Re-apply display mode to the currently loaded snapshot"

    def execute(self, context):
        settings = context.scene.astrosim_settings
        snapshot_path = Path(settings.active_snapshot_path) if settings.active_snapshot_path else None
        if snapshot_path is None or not snapshot_path.exists():
            self.report({"ERROR"}, "No active snapshot path is set. Use Load Latest Snapshot first.")
            return {"CANCELLED"}

        payload = load_display_payload(snapshot_path, settings.display_mode)
        update_preview_object(payload)
        self.report({"INFO"}, f"Display refreshed for frame {payload.frame}")
        return {"FINISHED"}
