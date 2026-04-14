"""Blender addon shell for the cinematic astrophysical simulation platform."""

from __future__ import annotations

bl_info = {
    "name": "Cinematic Astro Sim",
    "author": "Codex Scaffold",
    "version": (0, 1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Astro Sim",
    "description": "Thin Blender shell over a headless simulation core backed by Warp.",
    "category": "Simulation",
}

try:
    import bpy
except ImportError:  # pragma: no cover - Blender-only import path
    bpy = None

if bpy:
    from addon.operators import AstroSimRunPresetOperator
    from addon.props import ASTROSIM_Settings
    from addon.ui import ASTROSIM_PT_panel

    CLASSES = (ASTROSIM_Settings, AstroSimRunPresetOperator, ASTROSIM_PT_panel)

    def register():
        for cls in CLASSES:
            bpy.utils.register_class(cls)
        bpy.types.Scene.astrosim_settings = bpy.props.PointerProperty(type=ASTROSIM_Settings)

    def unregister():
        del bpy.types.Scene.astrosim_settings
        for cls in reversed(CLASSES):
            bpy.utils.unregister_class(cls)

else:
    CLASSES = ()

    def register():
        return None

    def unregister():
        return None
