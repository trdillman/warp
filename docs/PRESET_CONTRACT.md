# Preset Contract

Presets implement `PresetPlugin` from `sim_core/contracts.py`.

Required members:

- `meta: PresetMeta`
- `default_config() -> PresetConfig`
- `compile_spec(config) -> SimulationSpec`

Presets must not:

- import from `backends/`
- call Warp directly
- execute runtime loops

Presets are scenario definitions only.
