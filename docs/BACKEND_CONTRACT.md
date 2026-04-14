# Backend Contract

Backends implement `BackendAdapter` from `sim_core/contracts.py`.

Required methods:

- `initialize(spec)`
- `step(runtime_state, dt)`
- `snapshot(runtime_state, frame, time)`

Backend code belongs in `backends/<name>/` and should not leak into `presets/` or `addon/`.
