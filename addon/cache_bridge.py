from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from sim_core.cache_io import read_snapshot
from sim_core.contracts import PresetConfig


@dataclass(frozen=True)
class DisplayPayload:
    """Cache-derived particle payload used by Blender visualization code."""

    frame: int
    time: float
    positions: list[tuple[float, float, float]]
    colors: list[tuple[float, float, float, float]]


def find_latest_snapshot(cache_dir: Path) -> Path:
    """Return the latest frame snapshot from a cache directory."""

    candidates = sorted(cache_dir.glob("frame_*.json"))
    if not candidates:
        raise FileNotFoundError(f"No cache snapshots found in '{cache_dir}'.")
    return candidates[-1]


def build_preview_config(base: PresetConfig, preview_steps: int, preview_save_every: int) -> PresetConfig:
    """Build low-resolution preview overrides from a preset default config."""

    values = dict(base.values)
    values.update(
        {
            "earth_particles": min(int(values.get("earth_particles", 160)), 64),
            "theia_particles": min(int(values.get("theia_particles", 96)), 40),
            "settle_steps": min(int(values.get("settle_steps", 18)), 6),
            "default_steps": preview_steps,
            "save_every": preview_save_every,
        }
    )
    return PresetConfig(values=values)


def _normalize_scalars(values: list[float]) -> list[float]:
    if not values:
        return []
    v_min = min(values)
    v_max = max(values)
    if abs(v_max - v_min) < 1.0e-12:
        return [0.5 for _ in values]
    return [(v - v_min) / (v_max - v_min) for v in values]


def _colorize_ids(ids: list[int]) -> list[tuple[float, float, float, float]]:
    palette = [
        (0.95, 0.35, 0.35, 1.0),
        (0.35, 0.75, 0.95, 1.0),
        (0.95, 0.75, 0.35, 1.0),
        (0.65, 0.45, 0.95, 1.0),
        (0.35, 0.95, 0.6, 1.0),
        (0.95, 0.95, 0.35, 1.0),
    ]
    return [palette[int(item) % len(palette)] for item in ids]


def _colorize_density(densities: list[float]) -> list[tuple[float, float, float, float]]:
    normalized = _normalize_scalars([float(x) for x in densities])
    return [(x, 0.25, 1.0 - x, 1.0) for x in normalized]


def load_display_payload(snapshot_path: Path, display_mode: str) -> DisplayPayload:
    """Load a snapshot and map channels to display-ready particle colors."""

    state = read_snapshot(snapshot_path)
    positions = [tuple(map(float, pos)) for pos in state.positions]

    if display_mode == "material":
        colors = _colorize_ids(state.material_ids)
    elif display_mode == "density":
        colors = _colorize_density(state.densities)
    else:
        colors = _colorize_ids(state.provenance_ids)

    return DisplayPayload(frame=state.frame, time=state.time, positions=positions, colors=colors)
