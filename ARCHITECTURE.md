# Architecture Overview

This repository is a long-lived preset-driven simulation platform scaffold, not a one-off addon.

## Boundary map

- `addon/`: Blender shell only (UI, properties, operators).
- `sim_core/`: neutral contracts, preset compilation flow, runtime orchestration, IO/observability helpers.
- `backends/warp/`: Warp-specific compute implementation behind `BackendAdapter`.
- `presets/`: authored scenarios that compile to `SimulationSpec`.
- `io/`: file format contracts and schema docs.
- `scripts/`: composable developer tools.
- `tests/`: headless architecture and runtime guardrails.

## Data flow

1. A preset plugin receives config and compiles to `SimulationSpec`.
2. `SimulationRuntime` validates run settings, writes run manifest, and calls backend.
3. Backend initializes runtime buffers and performs stepping.
4. Runtime writes cache snapshots and run summary artifacts.
5. Blender calls the same runtime path via `sim_core.app`.

## Future node-system compatibility

A future node graph should compile to the same `SimulationSpec` contract.
The runtime and backend interfaces should remain unchanged when that happens.
