# Cinematic Astro Sim Blender Addon

Cinematic Astro Sim is a Windows-first Blender addon for previewing cinematic astrophysical simulations.

This repository keeps only the addon-facing code and release tooling:

- Blender addon UI and operators in `addon/`
- runtime contracts and cache IO in `sim_core/` and `io/`
- preset definitions in `presets/`
- a Warp-backed solver adapter in `backends/warp/`
- Windows release packaging in `scripts/build_blender_addon_zip.py`

## Install

### Build the Windows addon zip

```powershell
uv run scripts/build_blender_addon_zip.py
```

The build script downloads a pinned Windows `warp-lang` wheel from PyPI unless you override it with
`ASTROSIM_WARP_RUNTIME_WHEEL` or `--runtime-wheel`.

Artifacts:

- `dist/cinematic_astro_sim_blender_addon-vX.Y.Z-windows.zip`
- `dist/cinematic_astro_sim_blender_addon-vX.Y.Z-windows.zip.sha256`

### Install in Blender

1. Open `Edit > Preferences > Add-ons`.
2. Click `Install...`.
3. Select the generated zip.
4. Enable `Cinematic Astro Sim`.

The release zip bundles the Windows Warp runtime, so Blender does not need a separate repo-local `warp/` checkout.

## Run

1. Open the `Astro Sim` panel in the 3D View sidebar.
2. Choose `Moon Birth / Theia Impact`.
3. Leave `Use Preview Mode` enabled.
4. Click `Run Preview`.
5. Use `Load Latest Snapshot` and `Refresh Display` to inspect cached frames.

## Developer Notes

- Override the bundled runtime source with `ASTROSIM_WARP_RUNTIME_WHEEL=<path-to-wheel>` for offline or repeatable local builds.
- Run tests with `python -m unittest tests.test_repo_layout tests.test_blender_packaging tests.test_cache_visualization_prep`.
- The repo intentionally does not vendor the upstream `warp/` source tree.

## Documentation

- `ARCHITECTURE.md`
- `docs/BLENDER_QUICKSTART.md`
- `docs/BLENDER_MANUAL_TEST.md`
- `docs/RELEASING.md`
- `docs/BACKEND_CONTRACT.md`
- `docs/BLENDER_INTEGRATION_BOUNDARY.md`
- `docs/PRESET_CONTRACT.md`
- `docs/SIMULATION_SPEC.md`
- `docs/MOON_BIRTH_MODEL.md`
- `docs/MOON_BIRTH_LIMITATIONS.md`
- `docs/RUN_DIAGNOSTICS.md`
