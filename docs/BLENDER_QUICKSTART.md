# Blender Quickstart

This is the fastest path to build, install, and run the Windows addon package.

## 1) Build the installable addon zip

```powershell
uv run scripts/build_blender_addon_zip.py
```

Expected artifacts:

- `dist/cinematic_astro_sim_blender_addon-vX.Y.Z-windows.zip`
- `dist/cinematic_astro_sim_blender_addon-vX.Y.Z-windows.zip.sha256`

The packaging script downloads a pinned Windows `warp-lang` wheel unless you override it with:

- `ASTROSIM_WARP_RUNTIME_WHEEL`
- `uv run scripts/build_blender_addon_zip.py --runtime-wheel <path>`

## 2) Install in Blender

1. Open Blender.
2. Go to `Edit > Preferences > Add-ons`.
3. Click `Install...`.
4. Select `dist/cinematic_astro_sim_blender_addon-vX.Y.Z-windows.zip`.
5. Enable `Cinematic Astro Sim`.

## 3) Run a first preview

1. Open a 3D Viewport and press `N` to open the sidebar.
2. Open the `Astro Sim` tab.
3. Select preset `Moon Birth / Theia Impact`.
4. Keep `Use Preview Mode` enabled.
5. Click `Run Preview`.

When the run completes, the addon creates or updates `AstroSimPreview` from the latest cache snapshot.

## 4) Reload and recolor

- Click `Load Latest Snapshot` to reload the newest cached frame.
- Change `Display By` to `Provenance`, `Material`, or `Density`.
- Click `Refresh Display` to apply the selected color mode.

## Output paths

- Snapshots are written to `<output_dir>/cache/frame_XXXXX.json`.
- Diagnostics are written to `<output_dir>/diagnostics/frame_XXXXX.json`.
- The active snapshot path is stored in scene settings so reload and recolor do not require a rerun.
