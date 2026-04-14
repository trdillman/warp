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
    "densities",
    "internal_energy",
    "smoothing_lengths",
    "material_ids",
    "provenance_ids",
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
    vector_keys = ["velocities"]
    scalar_keys = ["masses", "densities", "internal_energy", "smoothing_lengths", "material_ids", "provenance_ids"]

    for key in vector_keys + scalar_keys:
        if len(payload[key]) != particle_count:
            raise CacheValidationError(f"{key} length must match positions length.")


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
        "densities": state.densities,
        "internal_energy": state.internal_energy,
        "smoothing_lengths": state.smoothing_lengths,
        "material_ids": state.material_ids,
        "provenance_ids": state.provenance_ids,
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
        densities=payload["densities"],
        internal_energy=payload["internal_energy"],
        smoothing_lengths=payload["smoothing_lengths"],
        material_ids=payload["material_ids"],
        provenance_ids=payload["provenance_ids"],
    )
