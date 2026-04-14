from __future__ import annotations

import bpy

from presets import list_preset_metadata


def preset_items(_self, _context):
    return [(meta.preset_id, meta.display_name, meta.description) for meta in list_preset_metadata()]


class ASTROSIM_Settings(bpy.types.PropertyGroup):
    preset_id: bpy.props.EnumProperty(
        name="Preset",
        description="Simulation preset",
        items=preset_items,
        default="moon_birth_theia",
    )
    steps: bpy.props.IntProperty(name="Steps", default=220, min=1, max=5000)
    dt: bpy.props.FloatProperty(name="Delta Time", default=0.01, min=1.0e-5)
    save_every: bpy.props.IntProperty(name="Save Every", default=5, min=1, max=5000)
    output_dir: bpy.props.StringProperty(name="Output Dir", default="/tmp/astrosim", subtype="DIR_PATH")
    display_mode: bpy.props.EnumProperty(
        name="Display By",
        items=[
            ("provenance", "Provenance", "Color by source body and layer"),
            ("material", "Material", "Color by material"),
            ("density", "Density", "Color by density proxy"),
        ],
        default="provenance",
    )
