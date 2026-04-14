# Moon FX Addon UX, Live Testing, and Runtime Plan

## Scope

Capture the implementation direction from the Moon FX Blender add-on session so future work can continue without rediscovering the testing and UX strategy.

## Current Staged Plan

1. `todo` Reliability foundation
   - Add shared operator-safe error handling.
   - Convert runtime failures into user-facing Blender reports instead of raw tracebacks.
   - Keep stale Blender RNA references self-healing where safe.
   - Surface a structured addon status model (`ok`, `warning`, `blocked`, `last_error`, `reinit_required`).

2. `todo` Live parameter architecture
   - Add `update=` callbacks to relevant Blender properties.
   - Route edits through a central `runtime.on_settings_changed(...)`.
   - Classify parameters as `live`, `deferred_next_frame`, or `requires_reinit`.
   - Make gravity, damping, delta time, point radius, and similar cheap knobs respond during playback.

3. `todo` Panel redesign for technical users
   - Keep all major controls available for power users.
   - Reorganize the panel into `Status`, `Quick Actions`, `Live Tuning`, `Advanced`, and `Diagnostics`.
   - Annotate or gray out irrelevant controls instead of hiding capability.
   - Add `Validate Setup`, `Run Smoke Test`, and `Copy Debug Report`.

4. `todo` GUI and headless validation
   - Preserve the existing headless integration tests as baseline verification.
   - Add reusable GUI-loaded validation through the `blender-addon-live-testing` skill.
   - Add tests for live parameter updates while playback is running.
   - Keep block-dim benchmarking isolated per Blender process.

5. `todo` Quality-of-life polish
   - Add explicit recovery notices when scene artifacts are rebuilt automatically.
   - Add one-click repair actions for point cloud and Geometry Nodes preview setup.
   - Add safer preset loading guidance for interactive sessions.

## Immediate Next Implementation Slice

1. `todo` Add shared operator exception handling and last-error reporting.
2. `todo` Add preflight/status box at the top of the addon panel.
3. `todo` Implement live updates for gravity, damping, and point radius first.
4. `todo` Mark structural settings like `particle_count`, `solver`, `seed`, and `block_dim` as reinit-required.
5. `todo` Convert the current block-dim benchmark into a repeatable diagnostic entry point or smoke-test extension.

## Notes

- `block_dim` is currently a performance knob only; it should remain under `Advanced`.
- Benchmarks on the current CUDA device favored `256` for `SPH_IMPACT` and `FLIP_CYCLONE`, but `32` for `BARNES_HUT_EXTREME`.
- The current addon still has a harmless Blender MCP GN snapshot export warning when Geometry Nodes modifiers are edited through the live MCP workflow.
