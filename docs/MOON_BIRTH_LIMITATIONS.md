# Moon Birth Limitations

This implementation is intentionally VFX-oriented and not publication-grade.

## Simplifications

- EOS is analytic and approximate (no full ANEOS / M-ANEOS workflow)
- Self-gravity is softened all-pairs (not a scalable tree/FMM yet)
- SPH formulation is baseline and intended as replaceable
- Settling is damping-based relaxation, not full hydrostatic solve
- Diagnostics use approximate orbital-energy/angular-momentum classification

## Not covered

- Long-term disk evolution and moon accretion timescales
- Full thermodynamic phase behavior realism
- Detailed shock/phase calibration against planetary-impact literature

## Why acceptable here

- Objective is cinematic plausibility and robust authoring workflow
- Architecture keeps clear extension points for future fidelity upgrades
