from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from sim_core.contracts import SimulationSpec, SimulationState


def classify_debris(state: SimulationState, spec: SimulationSpec) -> dict[str, float | dict[str, float]]:
    """Classify mass budget into merged body, bound debris, disk candidates, and escape."""

    pos = np.asarray(state.positions, dtype=np.float64)
    vel = np.asarray(state.velocities, dtype=np.float64)
    mass = np.asarray(state.masses, dtype=np.float64)
    provenance = np.asarray(state.provenance_ids, dtype=np.int32)
    material = np.asarray(state.material_ids, dtype=np.int32)

    total_mass = float(np.sum(mass))
    if total_mass <= 0:
        return {}

    com = np.sum(pos * mass[:, None], axis=0) / total_mass
    vcom = np.sum(vel * mass[:, None], axis=0) / total_mass

    rel_pos = pos - com[None, :]
    rel_vel = vel - vcom[None, :]
    r = np.linalg.norm(rel_pos, axis=1)
    v2 = np.sum(rel_vel * rel_vel, axis=1)

    g_mu = float(np.sum(mass))
    eps = float(spec.solver_config.get("gravity_softening", 0.08))
    specific_energy = 0.5 * v2 - g_mu / np.sqrt(r * r + eps * eps)

    central_radius = float(spec.diagnostics_config.get("central_radius_estimate", 1.2))
    roche_limit = float(spec.diagnostics_config.get("roche_limit", 2.5))

    bound = specific_energy < 0.0
    escaping = ~bound
    central = bound & (r <= central_radius)
    orbiting = bound & (r > central_radius)
    disk_candidate = orbiting & (r <= roche_limit * 2.0)

    def mass_of(mask):
        return float(np.sum(mass[mask]))

    orbiting_mass = mass_of(orbiting)
    iron_orbiting = mass_of(orbiting & (material == 1))

    provenance_labels = {p.provenance_id: p.name for p in spec.provenances}
    provenance_mass: dict[str, float] = {}
    if orbiting_mass > 0:
        for pid, name in provenance_labels.items():
            provenance_mass[name] = mass_of(orbiting & (provenance == pid)) / orbiting_mass

    angular_momentum = np.sum(np.cross(rel_pos, rel_vel) * mass[:, None], axis=0)

    return {
        "total_mass": total_mass,
        "merged_main_body_mass": mass_of(central),
        "bound_circumterrestrial_mass": orbiting_mass,
        "escaping_mass": mass_of(escaping),
        "disk_candidate_mass": mass_of(disk_candidate),
        "outside_main_body_mass": mass_of(r > central_radius),
        "iron_fraction_in_orbiting": float(iron_orbiting / orbiting_mass) if orbiting_mass > 0 else 0.0,
        "provenance_fractions_orbiting": provenance_mass,
        "angular_momentum": {
            "x": float(angular_momentum[0]),
            "y": float(angular_momentum[1]),
            "z": float(angular_momentum[2]),
        },
        "roche_limit": roche_limit,
    }


def write_diagnostics(path: Path, diagnostics: dict) -> None:
    """Write diagnostics JSON artifact."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(diagnostics, indent=2), encoding="utf-8")
