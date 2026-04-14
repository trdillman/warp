# PLAN

## Completed in this pass

- [x] Replace placeholder Moon Birth path with a real SPH+gravity impact path
- [x] Add differentiated body initial-condition builder (core/mantle + provenance)
- [x] Add pre-impact settling stage and resume-from-cache support
- [x] Add adaptive timestep control in runtime loop
- [x] Add debris diagnostics and run artifacts
- [x] Keep architecture boundaries intact (preset -> SimulationSpec -> runtime -> backend)

## Next

- [ ] Improve stability/perf for larger particle counts
- [ ] Add optional gravity approximations beyond all-pairs
- [ ] Add richer Blender viewport playback utilities
- [ ] Add stricter JSON schema checks for diagnostics/manifest artifacts

## Later

- [ ] Table-backed EOS option (ANEOS-style architecture extension)
- [ ] Replaceable SPH variants (e.g., PSPH/DISPH-like path)
- [ ] Node-frontend compiler that emits `SimulationSpec`
