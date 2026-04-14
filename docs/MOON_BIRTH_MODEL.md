# Moon Birth Model (VFX-first)

This preset approximates a canonical giant-impact scenario:

- differentiated proto-Earth (iron-like core + silicate-like mantle)
- differentiated Theia-like impactor
- grazing impact geometry near ~45 degrees
- impact speed near mutual escape velocity multiple

## Implemented model components

- Particle hydrodynamics (SPH-style density + pressure + artificial viscosity)
- HashGrid neighbor search for local hydrodynamic interactions
- Softened all-pairs self-gravity
- Adaptive timestep controller (CFL, acceleration, displacement limiters)
- Pre-impact settling stage with damping for initial-condition relaxation
- Material and provenance tracking through outputs and diagnostics

## EOS used in this pass

- Analytic Tait-like EOS per material (silicate-like, iron-like)
- EOS architecture is table-ready but not ANEOS-complete in this pass

## Output focus

This simulation targets the first hours of deformation/ejection and disk-candidate debris emergence, not long-timescale lunar accretion.
