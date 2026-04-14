# Blender Manual Smoke Test

This smoke test verifies the first user-facing Blender milestone:
install addon -> run preview -> see particles -> reload -> change display mode.

## Preconditions

- Blender 4.0+
- Warp repository checkout
- `uv` available

## Steps

1. Build addon zip:
   - `uv run scripts/build_blender_addon_zip.py`
   - Verify `dist/cinematic_astro_sim_blender_addon.zip` exists.
2. Install addon from zip in Blender Preferences.
3. Enable `Cinematic Astro Sim`.
4. In a new scene, open `Astro Sim` sidebar panel.
5. Select preset `Moon Birth / Theia Impact`.
6. Confirm `Use Preview Mode` is enabled with low values (defaults are suitable).
7. Click `Run Preview`.
8. Wait for completion and verify `AstroSimPreview` appears in the scene.
9. Click `Load Latest Snapshot`; verify the same object updates from cache.
10. Set `Display By = Material`, click `Refresh Display`, verify colors change.
11. Set `Display By = Density`, click `Refresh Display`, verify colors change.
12. Set `Display By = Provenance`, click `Refresh Display`, verify colors change.

## Expected results

- Preview run finishes quickly compared to default full run.
- Cache files appear under `<output_dir>/cache/`.
- `AstroSimPreview` exists and updates when reloading/refreshing.
- Display mode affects colors.

## Known limitations for this milestone

- No polished cinematic shading path yet.
- No timeline playback operator yet; this pass supports latest-snapshot loading and refresh.
- Physics model remains VFX-first and approximate (see `docs/MOON_BIRTH_LIMITATIONS.md`).
