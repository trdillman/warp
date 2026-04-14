# PLAN

## Phase 1 (completed): Foundation

- [x] Establish repo boundaries (`addon/`, `sim_core/`, `backends/`, `presets/`, `io/`, `scripts/`, `tests/`)
- [x] Add shared runtime and Warp backend vertical slice
- [x] Add first preset (`moon_birth_theia`)

## Phase 2 (current): Harden architecture and continuity

- [x] Introduce neutral `SimulationSpec` contract
- [x] Make presets compile to `SimulationSpec`
- [x] Add second lightweight preset (`asteroid_belt_disruption`) using same plumbing
- [x] Add structured run manifest + human-readable summary artifacts
- [x] Add guardrail tests for boundary leakage and contract drift
- [x] Add developer scripts for list/validate/scaffold/inspect/spec-print
- [x] Document architecture and continuation rules in dedicated docs

## Phase 3 (next): Controlled feature growth

- [ ] Add restart-from-snapshot runner
- [ ] Add stronger parameter schema validation
- [ ] Add solver/force strategy slots (SPH, neighbor policy, gravity model variants)
- [ ] Add richer output channels and export adapters

## Phase 4 (future): Node-authoring compatibility

- [ ] Define node-compiler-to-`SimulationSpec` mapping contract
- [ ] Keep runtime/backend unchanged while adding node-based authoring frontend
