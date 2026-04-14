# NOTES

## Repo state in this pass

- Moon Birth path moved from simple gravity placeholder to real SPH+gravity impact path.
- Second preset remains lightweight and reuses same architecture.

## What is now real

- Differentiated body initialization with provenance/material IDs
- Pre-impact settling routine
- SPH-style density/pressure + artificial viscosity
- Softened self-gravity
- Adaptive timestep limiting
- Cache + diagnostics + run manifest outputs

## What remains simplified

- EOS is analytic, not ANEOS-complete
- Gravity is all-pairs, not scalable tree/FMM
- Debris classification is approximate and VFX-oriented

## Continuation hint

Prioritize stability/performance and diagnostics tooling before fidelity-heavy EOS/gravity upgrades.
