# Blender Quickstart

## Build installable addon zip

```bash
uv run scripts/build_blender_addon_zip.py
```

Expected artifact:

- `dist/cinematic_astro_sim_blender_addon.zip`

## Install in Blender

1. Open Blender.
2. Go to `Edit > Preferences > Add-ons`.
3. Click `Install...`.
4. Select `dist/cinematic_astro_sim_blender_addon.zip`.
5. Enable `Cinematic Astro Sim`.

## First preview run

1. Open a 3D viewport and press `N` for the sidebar.
2. Open the `Astro Sim` tab.
3. Keep `Use Preview Mode` enabled.
4. Click `Run Preview`.
5. After completion, the addon creates or updates `AstroSimPreview` with particles from the latest cache snapshot.

## Reload and recolor

- Click `Load Latest Snapshot` to reload the newest frame from cache.
- Change `Display By` to `Provenance`, `Material`, or `Density`.
- Click `Refresh Display` to apply the selected color mode.

## Output paths

- The run writes snapshots to `<output_dir>/cache/frame_XXXXX.json`.
- The addon stores the active snapshot and cache path in scene settings so reloading works without rerunning.
