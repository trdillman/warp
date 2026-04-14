# SimulationSpec Contract

`SimulationSpec` is the backend-agnostic intermediate representation.

Fields include:

- `spec_version`
- `preset_id`
- `particle_init`
- `materials`
- `solver_config`
- `runtime`
- `backend_requirements`
- `cache_settings`
- `visualization_hints`
- `parameter_defaults`

This contract is intentionally explicit so that both presets and future node-graph compilers target the same runtime input.
