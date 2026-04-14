# Cinematic Astrophysical Simulation Platform (Warp Backend)

This repository is the reusable core of a long-lived Blender addon platform for cinematic astrophysical simulations.

## Principles

- VFX plausibility over scientific fidelity
- Thin Blender shell, headless-first simulation core
- Presets compile into one neutral `SimulationSpec`
- Warp isolated behind backend contracts
- Explicit file-backed cache/restart + run observability artifacts

## Structure

- `addon/`: Blender registration, UI, and operators only
- `sim_core/`: contracts, runtime, IO validation, run observability
- `backends/warp/`: Warp kernels and adapter
- `presets/`: authored scenarios compiling to `SimulationSpec`
- `io/`: cache schema and IO docs
- `scripts/`: list/validate/run/scaffold/inspect tools
- `tests/`: headless runtime + architecture guardrails

## Presets currently available

- `moon_birth_theia`
- `asteroid_belt_disruption`

## Core flow

1. Preset plugin compiles config into `SimulationSpec`.
2. `SimulationRuntime` executes spec via `BackendAdapter`.
3. Backend steps simulation and emits snapshots.
4. Runtime writes cache snapshots + run manifest + summary.

## Quick commands

```bash
uv run scripts/list_presets.py
uv run scripts/validate_preset.py moon_birth_theia
uv run scripts/run_preset.py --preset-id moon_birth_theia --steps 12 --output-dir /tmp/astrosim
uv run scripts/inspect_cache.py /tmp/astrosim/cache/frame_00012.json
uv run -m unittest tests.test_vertical_slice tests.test_architecture_guardrails -v
```

## Adding a new preset

1. Scaffold: `uv run scripts/scaffold_preset.py <preset_id>`
2. Implement `PresetPlugin.compile_spec()` in `presets/<preset_id>.py`
3. Register in `presets/__init__.py`
4. Ensure Blender preset enum picks it up via metadata
5. Add/extend tests under `tests/`

See also:

- `ARCHITECTURE.md`
- `docs/PRESET_CONTRACT.md`
- `docs/SIMULATION_SPEC.md`
- `docs/BACKEND_CONTRACT.md`
- `docs/BLENDER_INTEGRATION_BOUNDARY.md`
- `docs/SESSION_CONTINUATION.md`
