# TODO

## Immediate

- [ ] Add `scripts/restart_run.py` for resume-from-cache workflow
- [ ] Add stricter per-preset parameter validation hooks
- [ ] Add JSON schema check script for run manifests
- [ ] Add Blender operator for snapshot inspection/import

## Near-term

- [ ] Add force/solver strategy interface stubs in `sim_core/` (no heavy physics yet)
- [ ] Add material registry expansion for future EOS/table lookup paths
- [ ] Add benchmark/diagnostic script for repeatable runtime comparisons

## Later

- [ ] Prepare node-compiler integration contract that outputs `SimulationSpec`
- [ ] Add binary cache format option while preserving schema versioning
- [ ] Add richer visual export tooling (USD/geo channels)
