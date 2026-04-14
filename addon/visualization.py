from __future__ import annotations

import bpy

from .cache_bridge import DisplayPayload

_OBJECT_NAME = "AstroSimPreview"


def _ensure_pointcloud_object(payload: DisplayPayload) -> bpy.types.Object:
    if _OBJECT_NAME in bpy.data.objects:
        old_obj = bpy.data.objects[_OBJECT_NAME]
        old_data = old_obj.data
        bpy.data.objects.remove(old_obj, do_unlink=True)
        if old_data and old_data.users == 0:
            bpy.data.pointclouds.remove(old_data)

    pointcloud = bpy.data.pointclouds.new(_OBJECT_NAME)
    pointcloud.points.add(len(payload.positions))

    flat_positions = [c for xyz in payload.positions for c in xyz]
    pointcloud.points.foreach_set("co", flat_positions)

    color_attr = pointcloud.attributes.get("color")
    if color_attr is None:
        color_attr = pointcloud.attributes.new("color", "FLOAT_COLOR", "POINT")
    color_attr.data.foreach_set("color", [c for rgba in payload.colors for c in rgba])

    obj = bpy.data.objects.new(_OBJECT_NAME, pointcloud)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def _ensure_mesh_object(payload: DisplayPayload) -> bpy.types.Object:
    mesh = bpy.data.meshes.get(_OBJECT_NAME)
    if mesh is None:
        mesh = bpy.data.meshes.new(_OBJECT_NAME)
    mesh.clear_geometry()
    mesh.from_pydata(payload.positions, [], [])
    mesh.update()

    attr = mesh.color_attributes.get("color")
    if attr is None:
        attr = mesh.color_attributes.new(name="color", type="FLOAT_COLOR", domain="POINT")
    attr.data.foreach_set("color", [c for rgba in payload.colors for c in rgba])

    obj = bpy.data.objects.get(_OBJECT_NAME)
    if obj is None:
        obj = bpy.data.objects.new(_OBJECT_NAME, mesh)
        bpy.context.scene.collection.objects.link(obj)
    else:
        obj.data = mesh

    obj.display_type = "WIRE"
    return obj


def update_preview_object(payload: DisplayPayload) -> bpy.types.Object:
    """Create or update the Blender object holding preview particles."""

    if hasattr(bpy.data, "pointclouds"):
        obj = _ensure_pointcloud_object(payload)
    else:
        obj = _ensure_mesh_object(payload)

    obj["astrosim_frame"] = payload.frame
    obj["astrosim_time"] = payload.time
    return obj
