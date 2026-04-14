# START HERE

For a fresh contributor or Codex session:

1. Read in this order:
   - `README.md`
   - `ARCHITECTURE.md`
   - `DECISIONS.md`
   - `docs/SIMULATION_SPEC.md`
   - `docs/PRESET_CONTRACT.md`
2. Inspect preset inventory:
   - `uv run scripts/list_presets.py`
3. Validate and run one preset:
   - `uv run scripts/validate_preset.py moon_birth_theia`
   - `uv run scripts/run_preset.py --preset-id moon_birth_theia --steps 8 --output-dir /tmp/astrosim`
4. Inspect output:
   - `uv run scripts/inspect_cache.py /tmp/astrosim/cache/frame_00008.json`
5. Run tests:
   - `uv run -m unittest tests.test_vertical_slice tests.test_architecture_guardrails -v`

## Non-negotiables

- Do not bypass `SimulationSpec`.
- Do not move simulation logic into `addon/`.
- Do not call Warp from presets or Blender code.
- Do not redesign architecture without recording a decision in `DECISIONS.md`.

## How presets work

- Presets are thin scenario plugins.
- Each preset compiles config into `SimulationSpec`.
- Runtime executes the spec headlessly and Blender uses the same path.

## Future node-based direction

A future node authoring layer should compile into `SimulationSpec`; it should not replace runtime or backend contracts.

## Next milestones (in order)

1. Harden schema/validation and restart tooling.
2. Expand observability and run diagnostics.
3. Add more presets through the same compile-to-spec path.
4. Add optional force/solver strategy interfaces without breaking `SimulationSpec` contract.
