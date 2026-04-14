from __future__ import annotations

import json
from pathlib import Path

from sim_core.contracts import CACHE_SCHEMA_VERSION, SimulationState

REQUIRED_KEYS = {
    "schema_version",
    "frame",
    "time",
    "positions",
    "velocities",
    "masses",
    "materials",
}


class CacheValidationError(ValueError):
    """Raised when snapshot files do not follow the declared cache contract."""


def validate_snapshot_payload(payload: dict) -> None:
    """Validate payload shape for the current snapshot schema version."""

    missing = REQUIRED_KEYS.difference(payload.keys())
    if missing:
        raise CacheValidationError(f"Snapshot payload missing required keys: {sorted(missing)}")

    if payload["schema_version"] != CACHE_SCHEMA_VERSION:
        raise CacheValidationError(
            f"Unsupported snapshot schema_version '{payload['schema_version']}'. Expected '{CACHE_SCHEMA_VERSION}'."
        )

    if not isinstance(payload["frame"], int) or payload["frame"] < 0:
        raise CacheValidationError("Snapshot frame must be a non-negative integer.")

    if not isinstance(payload["time"], (int, float)):
        raise CacheValidationError("Snapshot time must be numeric.")

    particle_count = len(payload["positions"])
    if len(payload["velocities"]) != particle_count or len(payload["masses"]) != particle_count:
        raise CacheValidationError("positions, velocities, and masses must have matching lengths.")

    if len(payload["materials"]) != particle_count:
        raise CacheValidationError("materials length must match positions length.")


def write_snapshot(path: Path, state: SimulationState) -> None:
    """Write a simulation snapshot as JSON."""

    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": state.schema_version,
        "frame": state.frame,
        "time": state.time,
        "positions": state.positions,
        "velocities": state.velocities,
        "masses": state.masses,
        "materials": state.materials,
    }
    validate_snapshot_payload(payload)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def read_snapshot(path: Path) -> SimulationState:
    """Read a simulation snapshot from JSON."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    validate_snapshot_payload(payload)
    return SimulationState(
        schema_version=str(payload["schema_version"]),
        frame=int(payload["frame"]),
        time=float(payload["time"]),
        positions=payload["positions"],
        velocities=payload["velocities"],
        masses=payload["masses"],
        materials=payload["materials"],
    )
