from __future__ import annotations

import bpy

from presets import list_preset_metadata


def preset_items(_self, _context):
    items = []
    for meta in list_preset_metadata():
        items.append((meta.preset_id, meta.display_name, meta.description))
    return items


class ASTROSIM_Settings(bpy.types.PropertyGroup):
    preset_id: bpy.props.EnumProperty(
        name="Preset",
        description="Simulation preset",
        items=preset_items,
        default="moon_birth_theia",
    )
    steps: bpy.props.IntProperty(name="Steps", default=24, min=1, max=5000)
    dt: bpy.props.FloatProperty(name="Delta Time", default=0.05, min=1.0e-5)
    output_dir: bpy.props.StringProperty(name="Output Dir", default="/tmp/astrosim", subtype="DIR_PATH")
    save_every: bpy.props.IntProperty(name="Save Every", default=3, min=1, max=5000)
