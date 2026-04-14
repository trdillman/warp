# Releasing the Blender Addon

This repository publishes a **standalone Blender addon zip** that includes the embedded simulation core.

## Version source of truth

Release version is `bl_info["version"]` in `addon/__init__.py`.
`ADDON_VERSION` is derived from the same source.

- Example: `(0, 2, 0)` -> `0.2.0`
- Release tag must match this version.

## Build locally

```bash
uv run scripts/build_blender_addon_zip.py
```

Outputs:

- `dist/cinematic_astro_sim_blender_addon-vX.Y.Z.zip`
- `dist/cinematic_astro_sim_blender_addon-vX.Y.Z.zip.sha256`

Keep this artifact naming unchanged so local builds, CI uploads, and GitHub release assets remain aligned.

Optional utilities:

```bash
uv run scripts/build_blender_addon_zip.py --print-version
uv run scripts/build_blender_addon_zip.py --output /tmp/custom-addon.zip
```

## Tag format

Use addon tags:

- `addon-vX.Y.Z`

Example:

- `addon-v0.2.0`

On tagged pushes, CI validates tag/version parity.

## GitHub Actions workflow

- Workflow: `.github/workflows/blender-addon-release.yml`
- Triggers:
  - `workflow_dispatch`
  - push tag matching `addon-v*`

Behavior:

1. Resolve version from `addon/__init__.py`.
2. Build zip + checksum via `scripts/build_blender_addon_zip.py`.
3. Upload assets to workflow artifacts.
4. On tag pushes, publish GitHub Release with both assets.

## Manual release checklist

1. Update `bl_info["version"]` in `addon/__init__.py`.
2. Commit and push.
3. Create and push matching tag:
   - `git tag addon-vX.Y.Z`
   - `git push origin addon-vX.Y.Z`
4. Wait for `Blender Addon Release` workflow to finish.
5. Verify release assets include zip and checksum.

## Expected release assets

- `cinematic_astro_sim_blender_addon-vX.Y.Z.zip`
- `cinematic_astro_sim_blender_addon-vX.Y.Z.zip.sha256`
