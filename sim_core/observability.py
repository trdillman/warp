from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def write_run_manifest(path: Path, manifest: dict[str, Any]) -> None:
    """Write structured run manifest for observability and restart traceability."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def write_run_summary(path: Path, *, preset_id: str, backend: str, steps: int, dt: float, snapshots: int) -> None:
    """Write a short human-readable run summary."""

    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "Astro Sim Run Summary",
        f"preset_id: {preset_id}",
        f"backend: {backend}",
        f"steps: {steps}",
        f"dt: {dt}",
        f"snapshots_written: {snapshots}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
