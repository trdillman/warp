# Preset Contract

Presets implement `PresetPlugin` and must provide:

- `meta: PresetMeta`
- `default_config() -> PresetConfig`
- `compile_spec(config) -> SimulationSpec`

Rules:

- Presets author scenarios only.
- Presets do not import Warp or backend modules.
- Presets do not execute runtime stepping.
