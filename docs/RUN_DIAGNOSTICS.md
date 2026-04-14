# Run Diagnostics

Diagnostics are written to `<output_dir>/diagnostics/frame_XXXXX.json`.

Current fields include:

- `merged_main_body_mass`
- `bound_circumterrestrial_mass`
- `escaping_mass`
- `disk_candidate_mass`
- `outside_main_body_mass`
- `iron_fraction_in_orbiting`
- `provenance_fractions_orbiting`
- `angular_momentum`
- `roche_limit`
- `dt_limiter_counts`

Classification is based on simple specific orbital energy and radial thresholds around an estimated central-body radius.
These metrics are intended for VFX sanity checks, not rigorous astrophysical inference.
