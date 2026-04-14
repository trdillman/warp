# Blender Integration Boundary

`addon/` should remain a thin shell:

- expose preset selection and runtime parameters
- build a `SimulationRunRequest`
- call shared runtime entrypoints in `sim_core.app`

Do not put simulation algorithms, backend selection logic, or file-format rules in Blender classes.
