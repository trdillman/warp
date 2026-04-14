# Cinematic Astrophysical Simulation Platform (Warp Backend)

This repository is the reusable core of a long-lived Blender addon platform for cinematic astrophysical simulations.

## Current status

The `moon_birth_theia` preset now runs a first real VFX-oriented giant-impact path:

- differentiated proto-Earth + Theia initialization
- pre-impact settling stage
- SPH-style hydrodynamics with HashGrid neighbor search
- softened self-gravity
- adaptive timestep limiting
- restartable cache snapshots with material/provenance channels
- debris diagnostics and run manifests

## Architecture boundaries

- `addon/`: Blender shell only
- `sim_core/`: contracts, runtime, diagnostics, IO validation, initial conditions
- `backends/warp/`: Warp kernels + adapter
- `presets/`: scenario authorship compiling into `SimulationSpec`
- `io/`: schema and format docs
- `scripts/`: headless run and inspection tools
- `tests/`: solver path + architecture guardrails

## Quick commands

```bash
uv run scripts/build_blender_addon_zip.py
uv run scripts/list_presets.py
uv run scripts/validate_preset.py moon_birth_theia
uv run scripts/run_preset.py --preset-id moon_birth_theia --steps 40 --output-dir /tmp/astrosim --print-spec
uv run scripts/inspect_cache.py /tmp/astrosim/cache/frame_00040.json
uv run -m unittest tests.test_initial_conditions tests.test_vertical_slice tests.test_settling_and_resume tests.test_architecture_guardrails -v
```

## Core docs

- `ARCHITECTURE.md`
- `docs/SIMULATION_SPEC.md`
- `docs/PRESET_CONTRACT.md`
- `docs/BACKEND_CONTRACT.md`
- `docs/MOON_BIRTH_MODEL.md`
- `docs/MOON_BIRTH_LIMITATIONS.md`
- `docs/RUN_DIAGNOSTICS.md`
- `docs/BLENDER_QUICKSTART.md`
- `docs/BLENDER_MANUAL_TEST.md`
- `docs/RELEASING.md`
