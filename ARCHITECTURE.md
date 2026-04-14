# Addon Architecture Overview

This repository is organized as a Blender addon project with a bundled Windows Warp runtime in release artifacts.

## Runtime flow

1. A preset compiles to a `SimulationSpec`.
2. `SimulationRuntime` executes adaptive steps and writes cache snapshots.
3. The Warp backend in `backends/warp/` runs the SPH + gravity integration.
4. The addon loads snapshots and refreshes viewport preview objects.

## Boundaries

- `addon/`
  - Blender operators, panels, and scene settings.
  - Must stay focused on Blender UX and snapshot display.
- `sim_core/`
  - Runtime orchestration, contracts, diagnostics, and snapshot writing.
  - Owns interfaces shared by presets, addon code, and compute backends.
- `backends/warp/`
  - Warp-specific execution adapter.
  - Assumes a packaged `warp` runtime is available at import time.
- `presets/`
  - Authored simulation scenarios compiled into runtime specs.
- `io/`
  - Cache schema and compatibility expectations.
- `scripts/build_blender_addon_zip.py`
  - Release packaging entrypoint.
  - Downloads or reuses a pinned Windows Warp wheel and bundles the `warp/` package into the addon zip.

## Packaging model

- The repo does not vendor upstream Warp source code.
- The Windows release artifact is self-contained and bundles the pinned Warp runtime from an external wheel.
- Local development can override the pinned wheel with `ASTROSIM_WARP_RUNTIME_WHEEL` or `--runtime-wheel`.

## Snapshot handoff

- Cache snapshots live at `<output_dir>/cache/frame_XXXXX.json`.
- These snapshots are the interface between the simulation runtime and Blender display code.
- Display coloring (`Material`, `Provenance`, `Density`) depends on channels preserved in those cache files.
