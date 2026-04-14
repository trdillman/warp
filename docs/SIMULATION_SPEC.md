# SimulationSpec Contract

`SimulationSpec` is the backend-agnostic intermediate representation consumed by runtime/backends.

Current required sections:

- scenario identity (`preset_id`, `spec_version`)
- body setup (`body_configs`)
- particle payload (`particle_init`)
- materials/provenance (`materials`, `provenances`)
- EOS and solver config (`eos_config`, `solver_config`)
- runtime/timestep controls (`runtime`)
- backend requirements (`backend_requirements`)
- cache/output controls (`cache_settings`)
- diagnostics controls (`diagnostics_config`)
- settling controls (`settle_config`)
- visualization hints (`visualization_hints`)

Presets must compile into this contract.
Runtime executes this contract.
Backends consume this contract.
Future node-graph compilers should emit this contract.
