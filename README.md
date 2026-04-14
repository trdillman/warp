# Cinematic Astro Sim Blender Addon

Cinematic Astro Sim is a Blender addon for running and previewing cinematic astrophysical simulations.
This repository packages:

- a Blender-facing addon shell (`addon/`)
- simulation contracts/runtime (`sim_core/`)
- a Warp backend (`backends/warp/`)
- preset authorship (`presets/`)
- cache/manifest IO contracts (`io/`)

## Install

### Prerequisites

- Blender 4.0+
- `uv`

### Build addon zip

```bash
uv run scripts/build_blender_addon_zip.py
```

Artifacts:

- `dist/cinematic_astro_sim_blender_addon-vX.Y.Z.zip`
- `dist/cinematic_astro_sim_blender_addon-vX.Y.Z.zip.sha256`

### Install in Blender

1. Open `Edit > Preferences > Add-ons`.
2. Click `Install...` and select the generated zip.
3. Enable `Cinematic Astro Sim`.

## Run

### Preview run from Blender

1. Open the `Astro Sim` panel (N-sidebar).
2. Choose preset `Moon Birth / Theia Impact`.
3. Keep `Use Preview Mode` enabled.
4. Click `Run Preview`.
5. Use `Load Latest Snapshot` and `Refresh Display` to inspect cached results.

### Optional headless run

```bash
uv run scripts/run_preset.py --preset-id moon_birth_theia --steps 40 --output-dir /tmp/astrosim --print-spec
uv run scripts/inspect_cache.py /tmp/astrosim/cache/frame_00040.json
```

## Documentation

- `ARCHITECTURE.md`
- `docs/BLENDER_QUICKSTART.md`
- `docs/BLENDER_MANUAL_TEST.md`
- `docs/RELEASING.md`
- `docs/MOON_BIRTH_MODEL.md`
- `docs/MOON_BIRTH_LIMITATIONS.md`
- `docs/RUN_DIAGNOSTICS.md`
