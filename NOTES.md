# NOTES

## Current preset inventory

- `moon_birth_theia`
- `asteroid_belt_disruption`

Both compile to `SimulationSpec` and run through the same runtime/backend path.

## SimulationSpec observations

- Explicit sections (`particle_init`, `materials`, `solver_config`, `runtime`, `backend_requirements`, `cache_settings`) improve inspectability.
- The same IR can support future node-authoring by treating nodes as another compiler frontend.

## Guardrails added

- Tests enforce no backend leakage into `addon/` and `presets/`.
- Tests enforce preset compilation to `SimulationSpec`.
- Tests enforce cache schema version + required fields.

## Deferred work (intentional)

- Full multi-material SPH
- ANEOS/table fidelity
- Advanced long-range gravity and adaptive timestep research

These remain extension points, not this pass.
