---
context_id: moon-fx-addon-handoff-20260414-0352
label: Moon FX addon testing handoff
summary: Save the Moon FX addon installation, live Blender testing, runtime fixes, UX plan, and block-dim benchmark results for later continuation.
status: paused
session_kind: handoff
save_reason: handoff
created_at: 2026-04-14T07:52:13Z
updated_at: 2026-04-14T07:52:13Z
---

# Project Summary

- Primary repo for this save: `C:\Users\Tyler\Downloads\warp`
- Most actual work in this thread happened in sibling workspace `C:\Users\Tyler\Downloads\warp-main\warp-main\moon_fx_poc`
- Thread scope: Moon FX Blender add-on install, GUI-loaded validation, runtime fixes, Geometry Nodes preview work, UX planning, and headless `block_dim` benchmarking

# Active Goal

- Preserve the full Moon FX conversation context so a later session can continue implementation without rediscovering:
  - how the add-on was installed and validated
  - what runtime bugs were fixed
  - how live Blender MCP testing was made reliable
  - what staged UX/live-parameter plan was agreed
  - what `block_dim` measurements were observed

# Current Plan

Owner: main thread
Blocked By: none

1. `todo` Implement operator-safe error handling and user-facing error/status reporting.
2. `todo` Add preflight/status UI and diagnostics surface.
3. `todo` Add live property update architecture for safe runtime-editable parameters.
4. `todo` Keep all technical controls available, but move performance-only knobs like `block_dim` under advanced UX.
5. `todo` Expand test coverage to include live-parameter changes during playback and reusable diagnostic probes.

# Completed Work

- Saved the provided ZIP payload as `C:\Users\Tyler\Downloads\warp-main\warp-main\moon_fx_poc.zip`
- Extracted `moon_fx_poc`
- Installed `moon_fx_addon` into an isolated Blender profile and verified registration
- Added headless Blender integration coverage in `C:\Users\Tyler\Downloads\warp-main\warp-main\moon_fx_poc\tests\blender_integration_test.py`
- Fixed Blender 5.1 / Warp 1.12 compatibility issues in `runtime.py`
- Fixed stale cached point-cloud object handling by guarding invalid Blender RNA references
- Created reusable skill `C:\Users\Tyler\.codex\skills\blender-addon-live-testing\SKILL.md`
- Proved GUI-loaded addon testing through Blender MCP in a live Blender process
- Added a Geometry Nodes preview modifier on the point cloud with an exposed adjustable point radius
- Produced a staged UX/live-parameter implementation plan
- Benchmarked `block_dim` headlessly with isolated per-process probe runs and saved the aggregated report

# Touched Files and Subsystems

- Sibling prototype workspace:
  - `C:\Users\Tyler\Downloads\warp-main\warp-main\moon_fx_poc\blender_addon\moon_fx_addon\runtime.py`
  - `C:\Users\Tyler\Downloads\warp-main\warp-main\moon_fx_poc\tests\blender_integration_test.py`
  - `C:\Users\Tyler\Downloads\warp-main\warp-main\moon_fx_poc\tests\block_dim_benchmark.py`
  - `C:\Users\Tyler\Downloads\warp-main\warp-main\moon_fx_poc\tests\block_dim_probe.py`
  - `C:\Users\Tyler\Downloads\warp-main\warp-main\moon_fx_poc\outputs\blender_integration_report.json`
  - `C:\Users\Tyler\Downloads\warp-main\warp-main\moon_fx_poc\outputs\block_dim_benchmark_report.json`
  - `C:\Users\Tyler\Downloads\warp-main\warp-main\moon_fx_poc_blender_install_report.json`
- Skills and tooling:
  - `C:\Users\Tyler\.codex\skills\blender-addon-live-testing\SKILL.md`
  - `C:\Users\Tyler\.codex\skills\blender-addon-live-testing\agents\openai.yaml`

Subsystems:
- Blender add-on properties, operators, runtime, presets, panel layout
- Blender MCP live GUI control
- Headless Blender test harnesses
- Geometry Nodes preview setup for point clouds

# Commands and Validation

- Addon install and verify:
  - `uv run --no-project python C:\Users\Tyler\.codex\skills\blender-install\scripts\blender_install.py --addon-path C:\Users\Tyler\Downloads\warp-main\warp-main\moon_fx_poc\blender_addon\moon_fx_addon --report-path C:\Users\Tyler\Downloads\warp-main\warp-main\moon_fx_poc_blender_install_report.json`
- Headless integration suite:
  - `C:\Program Files\Blender Foundation\Blender 5.1\blender.exe --factory-startup --background --python C:\Users\Tyler\Downloads\warp-main\warp-main\moon_fx_poc\tests\blender_integration_test.py -- --report C:\Users\Tyler\Downloads\warp-main\warp-main\moon_fx_poc\outputs\blender_integration_report.json`
- Live GUI validation:
  - Blender MCP owned sessions were used successfully on `127.0.0.1:9877` and then a clean replay session on `127.0.0.1:9878`
- Block-dim smoke probe:
  - `C:\Program Files\Blender Foundation\Blender 5.1\blender.exe --factory-startup --background --python C:\Users\Tyler\Downloads\warp-main\warp-main\moon_fx_poc\tests\block_dim_probe.py -- --report C:\Users\Tyler\Downloads\warp-main\warp-main\moon_fx_poc\outputs\block_dim_probe_smoke.json --preset FLIP_CYCLONE --block-dim 256 --particle-count 4096`
- Full isolated benchmark matrix:
  - 3 presets × 5 block sizes × 3 repeats, one Blender process per run

Validation outcomes:
- Headless integration suite passed after runtime fixes
- GUI-loaded preset replay worked in a fresh MCP session
- `block_dim` benchmark completed successfully and produced a usable report

# Compile-Time and Environment Notes

- Blender version used: `5.1.0`
- Warp version observed in benchmarking and tests: `1.12.1`
- Current benchmark device recorded as `cuda:0`
- Isolated Blender profile used under:
  - `C:\Users\Tyler\Downloads\warp-main\warp-main\.blender_profile`
- Existing `warp` repo git state is unrelated to the prototype changes; `.codex/` is currently untracked there

# Problems

- The original GUI session on port `9877` accumulated stale addon/runtime state and became unreliable for reuse
- A real runtime bug existed: cached `STATE.point_object` could point at a removed Blender object and raise `ReferenceError: StructRNA of type Object has been removed`
- Repeated multi-config block-dim benchmarking inside a single Blender process crashed, so the benchmarking method had to switch to isolated one-config-per-process probes
- Live Geometry Nodes edits through Blender MCP still trigger a harmless GN snapshot export warning:
  - `Use either tree_name or object_name/modifier_name, not both.`

# What Worked

- Importing the addon from source inside a GUI-loaded Blender MCP session
- Re-registering the addon per test pass in disposable scenes
- Deterministic frame stepping using `scene.frame_set(...)` plus `runtime.on_frame_change(...)`
- Headless Blender integration tests with reduced particle counts
- Isolated per-process benchmarking for `block_dim`
- Exposing point radius through a Geometry Nodes modifier for easier viewport readability

# Open Risks and Questions

- The addon still lacks the user-facing error handling and preflight UX that was discussed
- Live property changes are not yet implemented; current behavior still depends on runtime reinit logic for many settings
- `block_dim` should remain an advanced tuning parameter until live UX is improved
- The Moon FX prototype lives in a sibling workspace, not in `C:\Users\Tyler\Downloads\warp`
- If future work continues in the prototype workspace, context should probably also be saved there to avoid split-state confusion

# Resume Steps

1. Start from `C:\Users\Tyler\Downloads\warp-main\warp-main\moon_fx_poc`, not the `warp` repo root, if continuing code changes.
2. Read `C:\Users\Tyler\Downloads\warp\.codex\context\plans\moon-fx-addon-ux-and-testing-plan-20260414.md`.
3. Review:
   - `C:\Users\Tyler\Downloads\warp-main\warp-main\moon_fx_poc\blender_addon\moon_fx_addon\runtime.py`
   - `C:\Users\Tyler\Downloads\warp-main\warp-main\moon_fx_poc\tests\blender_integration_test.py`
   - `C:\Users\Tyler\Downloads\warp-main\warp-main\moon_fx_poc\tests\block_dim_probe.py`
   - `C:\Users\Tyler\Downloads\warp-main\warp-main\moon_fx_poc\outputs\block_dim_benchmark_report.json`
4. Implement the first UX slice:
   - operator-safe error handling
   - last-error/status model
   - panel status/preflight box
5. Then implement live updates for gravity, damping, and point radius.

# Latest Git State

- Repo for this saved context: `C:\Users\Tyler\Downloads\warp`
- Branch: `main`
- Status at save time:
  - `## main...origin/main`
  - `?? .codex/`
- Latest commit:
  - `e8637cde (HEAD -> main, origin/main, origin/HEAD) Fix empty closure cell crash during eager hashing [GH-913]`

# Tracked Plan Docs

- `C:\Users\Tyler\Downloads\warp\.codex\context\plans\moon-fx-addon-ux-and-testing-plan-20260414.md`
  - Captures the staged UX/live-testing/runtime plan agreed during this session and the next recommended implementation slice.
