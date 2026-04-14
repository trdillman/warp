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
        layout.prop(settings, "steps")
        layout.prop(settings, "dt")
        layout.prop(settings, "save_every")
        layout.prop(settings, "output_dir")
        layout.operator("astrosim.run_preset")
