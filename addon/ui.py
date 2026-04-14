from __future__ import annotations

import bpy


class ASTROSIM_PT_panel(bpy.types.Panel):
    bl_label = "Astro Sim"
    bl_idname = "ASTROSIM_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Astro Sim"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.astrosim_settings

        layout.prop(settings, "preset_id")
        layout.prop(settings, "display_mode")
        layout.prop(settings, "output_dir")

        preview_box = layout.box()
        preview_box.label(text="Preview")
        preview_box.prop(settings, "use_preview")
        if settings.use_preview:
            preview_box.prop(settings, "preview_steps")
            preview_box.prop(settings, "preview_save_every")
        else:
            preview_box.prop(settings, "steps")
            preview_box.prop(settings, "dt")
            preview_box.prop(settings, "save_every")

        layout.operator("astrosim.run_preset", text="Run Preview" if settings.use_preview else "Run Simulation")
        layout.operator("astrosim.load_latest_snapshot")
        layout.operator("astrosim.refresh_display")

        if settings.active_snapshot_path:
            layout.label(text=f"Snapshot: {settings.active_snapshot_path}")
