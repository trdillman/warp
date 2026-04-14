# DECISIONS

## D-001: Keep Blender thin

Blender code builds requests and calls `sim_core` entrypoints only.

## D-002: Presets compile to SimulationSpec

Presets are scenario definitions; they do not execute backend logic directly.

## D-003: Moon Birth now uses real SPH+gravity path

The `moon_birth_theia` preset now runs neighbor-search hydrodynamics, softened self-gravity, adaptive dt, settling, and diagnostics.

Reason: move from scaffold placeholder to first actual cinematic giant-impact behavior.

## D-004: EOS is analytic and table-ready

Use analytic Tait-like EOS now; keep interface ready for future table-backed EOS.

Reason: deliver a working VFX model without pretending scientific ANEOS completeness.

## D-005: Diagnostics are explicit and honest

Diagnostics use simple energy/radius classification and are documented as approximate.

Reason: support VFX plausibility checks while avoiding false scientific claims.
