# Architecture Overview

This project is a preset-driven simulation platform.

## Runtime pipeline

1. Preset compiles into `SimulationSpec`.
2. `SimulationRuntime` executes with adaptive dt + artifact writing.
3. Backend (`backends/warp`) performs SPH + gravity stepping.
4. Cache + diagnostics artifacts are written for restart/inspection.
5. Blender addon reads cache snapshots and updates viewport preview objects.

## Boundary map

- `addon/`: UI shell only
- `sim_core/`: contracts, runtime, diagnostics, initial condition builders
- `backends/warp/`: compute kernels and adapter
- `presets/`: authored scenario compilation
- `io/`: schema docs

## Future node compatibility

A node system should compile to `SimulationSpec` without replacing runtime/backend contracts.
