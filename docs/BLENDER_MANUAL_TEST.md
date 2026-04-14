# Blender Manual Smoke Test

This smoke test validates the user-facing addon path:
install -> run preview -> verify particles -> reload -> verify display modes.

## Preconditions

- Blender 4.0+
- Cinematic Astro Sim Blender addon repository checkout
- `uv` available

## Test steps

1. Build addon zip:
   - `uv run scripts/build_blender_addon_zip.py`
   - Verify `dist/cinematic_astro_sim_blender_addon-vX.Y.Z.zip` exists.
   - Verify `dist/cinematic_astro_sim_blender_addon-vX.Y.Z.zip.sha256` exists.
2. Install the addon zip in Blender Preferences.
3. Enable `Cinematic Astro Sim`.
4. In a new scene, open the `Astro Sim` panel.
5. Select preset `Moon Birth / Theia Impact`.
6. Confirm `Use Preview Mode` is enabled.
7. Click `Run Preview`.
8. Verify `AstroSimPreview` appears after completion.
9. Click `Load Latest Snapshot`; verify the same object refreshes from cache.
10. Set `Display By = Material`, click `Refresh Display`, verify colors update.
11. Set `Display By = Density`, click `Refresh Display`, verify colors update.
12. Set `Display By = Provenance`, click `Refresh Display`, verify colors update.

## Expected results

- Preview run completes quickly compared to a full run.
- Cache files are present under `<output_dir>/cache/`.
- `AstroSimPreview` is created and updates on reload.
- Display mode changes color assignment.

## Known limitations

- Cinematic shading pipeline is not finalized.
- Timeline playback operator is not shipped in this milestone.
- Physics model is VFX-first and approximate (see `docs/MOON_BIRTH_LIMITATIONS.md`).
