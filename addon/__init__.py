from __future__ import annotations

import sys
from pathlib import Path

bl_info = {
    "name": "Cinematic Astro Sim",
    "author": "Codex Scaffold",
    "version": (0, 2, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Astro Sim",
    "description": "Thin Blender shell over a headless simulation core backed by Warp.",
    "category": "Simulation",
}

_THIS_DIR = Path(__file__).resolve().parent
_PARENT_DIR = _THIS_DIR.parent
for candidate in (_THIS_DIR, _PARENT_DIR):
    candidate_text = str(candidate)
    if candidate_text not in sys.path:
        sys.path.insert(0, candidate_text)

try:
    import bpy
except ImportError:  # pragma: no cover - Blender-only import path
    bpy = None

if bpy:
    from .operators import (
        AstroSimLoadLatestSnapshotOperator,
        AstroSimRefreshDisplayOperator,
        AstroSimRunPresetOperator,
    )
    from .props import ASTROSIM_Settings
    from .ui import ASTROSIM_PT_panel

    CLASSES = (
        ASTROSIM_Settings,
        AstroSimRunPresetOperator,
        AstroSimLoadLatestSnapshotOperator,
        AstroSimRefreshDisplayOperator,
        ASTROSIM_PT_panel,
    )

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
