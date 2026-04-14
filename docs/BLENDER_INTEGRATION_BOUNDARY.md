# Blender Integration Boundary

`addon/` remains a shell:

- select preset and run options
- build `SimulationRunRequest`
- call `sim_core.app.run_preset`

No hydrodynamics, gravity, EOS, or diagnostics logic should live in Blender UI code.
