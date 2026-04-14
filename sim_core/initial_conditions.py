from __future__ import annotations

import math
import random

from sim_core.contracts import BodyInitConfig, ParticleInit


def build_differentiated_body_particles(body: BodyInitConfig, rng: random.Random, base_h: float) -> ParticleInit:
    """Build differentiated spherical body particles with core/mantle layering and spin."""

    positions: list[list[float]] = []
    velocities: list[list[float]] = []
    masses: list[float] = []
    material_ids: list[int] = []
    provenance_ids: list[int] = []
    smoothing_lengths: list[float] = []
    internal_energy: list[float] = []

    core_count = int(body.particle_count * body.core_fraction)
    core_radius = body.radius * (body.core_fraction ** (1.0 / 3.0))

    total_mass_proxy = (
        (4.0 / 3.0)
        * math.pi
        * (core_radius**3 * body.core_density + (body.radius**3 - core_radius**3) * body.mantle_density)
    )
    particle_mass = total_mass_proxy / max(1, body.particle_count)

    for idx in range(body.particle_count):
        u = rng.random()
        v = rng.random()
        w = rng.random()

        theta = 2.0 * math.pi * u
        phi = math.acos(2.0 * v - 1.0)
        r = body.radius * (w ** (1.0 / 3.0))

        x = r * math.sin(phi) * math.cos(theta)
        y = r * math.sin(phi) * math.sin(theta)
        z = r * math.cos(phi)

        px = x + body.position[0]
        py = y + body.position[1]
        pz = z + body.position[2]

        spin_vx = body.spin[1] * pz - body.spin[2] * py
        spin_vy = body.spin[2] * px - body.spin[0] * pz
        spin_vz = body.spin[0] * py - body.spin[1] * px

        vx = body.velocity[0] + spin_vx
        vy = body.velocity[1] + spin_vy
        vz = body.velocity[2] + spin_vz

        in_core = idx < core_count and r <= core_radius

        positions.append([px, py, pz])
        velocities.append([vx, vy, vz])
        masses.append(particle_mass)
        material_ids.append(body.core_material_id if in_core else body.mantle_material_id)
        provenance_ids.append(body.core_provenance_id if in_core else body.mantle_provenance_id)
        smoothing_lengths.append(base_h)
        internal_energy.append(1.0 if in_core else 0.6)

    return ParticleInit(
        positions=positions,
        velocities=velocities,
        masses=masses,
        material_ids=material_ids,
        provenance_ids=provenance_ids,
        smoothing_lengths=smoothing_lengths,
        internal_energy=internal_energy,
    )


def merge_particle_inits(inits: list[ParticleInit]) -> ParticleInit:
    """Merge multiple body particle payloads into one initialization payload."""

    out = ParticleInit(
        positions=[],
        velocities=[],
        masses=[],
        material_ids=[],
        provenance_ids=[],
        smoothing_lengths=[],
        internal_energy=[],
    )
    for init in inits:
        out.positions.extend(init.positions)
        out.velocities.extend(init.velocities)
        out.masses.extend(init.masses)
        out.material_ids.extend(init.material_ids)
        out.provenance_ids.extend(init.provenance_ids)
        out.smoothing_lengths.extend(init.smoothing_lengths)
        out.internal_energy.extend(init.internal_energy)
    return out
