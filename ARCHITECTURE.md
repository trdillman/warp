# Addon Architecture Overview

This project is organized around clear boundaries between Blender UX, simulation runtime, compute backend, and persisted artifacts.

## Runtime flow

1. A preset compiles to a `SimulationSpec`.
2. `SimulationRuntime` executes adaptive steps and writes frame artifacts.
3. The Warp backend (`backends/warp/`) performs SPH + gravity integration.
4. Diagnostics/manifests/cache snapshots are emitted.
5. The Blender addon loads snapshots and updates viewport preview objects.

## Boundary map

- `addon/`
  - Blender operators, panels, and scene settings.
  - Must not embed solver internals.
- `sim_core/`
  - Runtime orchestration, contracts, diagnostics, initial conditions, and IO validation.
  - Defines interfaces consumed by addon and backends.
- `backends/warp/`
  - Warp-specific kernel and adapter implementation.
  - Conforms to `sim_core` backend contracts.
- `presets/`
  - Scenario authoring layer compiling authored parameters into `SimulationSpec`.
- `io/`
  - Cache/manifest schema and compatibility expectations.

## Presets and backends

Presets are backend-agnostic scenario definitions. Backends execute specs without changing preset semantics.
This keeps authored scenarios portable while allowing backend evolution.

## IO and diagnostics boundaries

- Cache snapshots (`<output_dir>/cache/frame_XXXXX.json`) are the handoff between runtime and addon display.
- Run manifests and diagnostics are runtime outputs for reproducibility, validation, and manual triage.
- Display coloring (`Material`, `Provenance`, `Density`) depends on shipped cache channels.

## Moon preset status

The shipped `moon_birth_theia` path is VFX-oriented and approximate by design.
See:

- `docs/MOON_BIRTH_MODEL.md`
- `docs/MOON_BIRTH_LIMITATIONS.md`
- `docs/RUN_DIAGNOSTICS.md`
