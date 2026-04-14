# START HERE

1. Read, in order:
   - `README.md`
   - `ARCHITECTURE.md`
   - `DECISIONS.md`
   - `docs/SIMULATION_SPEC.md`
   - `docs/MOON_BIRTH_MODEL.md`
   - `docs/MOON_BIRTH_LIMITATIONS.md`
2. Validate preset + run headless:
   - `uv run scripts/validate_preset.py moon_birth_theia`
   - `uv run scripts/run_preset.py --preset-id moon_birth_theia --steps 24 --output-dir /tmp/astrosim --print-spec`
3. Inspect artifacts:
   - `uv run scripts/inspect_cache.py /tmp/astrosim/cache/frame_00020.json`
   - read `/tmp/astrosim/diagnostics/*.json`
4. Run tests:
   - `uv run -m unittest tests.test_initial_conditions tests.test_vertical_slice tests.test_settling_and_resume tests.test_architecture_guardrails -v`

## Rules

- Keep Blender thin.
- Keep presets compiling to `SimulationSpec`.
- Keep Warp logic inside `backends/warp/`.
- Record architectural changes in `DECISIONS.md`.
- Do not claim scientific fidelity for this model.
