# Backend Contract

Backends implement `BackendAdapter` and must provide:

- `initialize(spec)`
- `initialize_from_state(spec, state)`
- `settle(runtime_state, spec)`
- `step(runtime_state, dt) -> step_stats`
- `snapshot(runtime_state, frame, time)`

Current Warp backend provides:

- SPH density/pressure kernels
- neighbor search via HashGrid
- softened all-pairs gravity
- integration + per-step dt stats
