# Releasing the Blender Addon

This project publishes a **standalone Blender addon zip** from the main repository.
No separate addon repository is required.

## Version source of truth

Addon release version comes from `bl_info["version"]` in `addon/__init__.py`.

- Example: `"version": (0, 2, 0)` -> `0.2.0`
- Release tag must match this version (see tag format below).

## Build locally

```bash
uv run scripts/build_blender_addon_zip.py
```

Outputs:

- `dist/cinematic_astro_sim_blender_addon-vX.Y.Z.zip`
- `dist/cinematic_astro_sim_blender_addon-vX.Y.Z.zip.sha256`

Optional utilities:

```bash
uv run scripts/build_blender_addon_zip.py --print-version
uv run scripts/build_blender_addon_zip.py --output /tmp/custom-addon.zip
```

## Tag format

Use addon-specific tags:

- `addon-vX.Y.Z`

Example:

- `addon-v0.2.0`

On tagged pushes, the workflow validates that tag version `X.Y.Z` matches `bl_info` version.

## GitHub Actions workflow

Workflow file:

- `.github/workflows/blender-addon-release.yml`

Triggers:

- Manual dispatch (`workflow_dispatch`)
- Push tags matching `addon-v*`

Behavior:

1. Resolve addon version from `addon/__init__.py`.
2. Build zip + checksum with `scripts/build_blender_addon_zip.py`.
3. Upload both files as workflow artifacts.
4. On tag pushes, create a GitHub Release and attach both assets.

The workflow opts into Node.js 24 for JavaScript-based actions via
`FORCE_JAVASCRIPT_ACTIONS_TO_NODE24=true` to avoid Node.js 20 deprecation issues.


## Manual release procedure

1. Update `bl_info["version"]` in `addon/__init__.py`.
2. Commit and push to main branch.
3. Create and push matching tag:
   - `git tag addon-vX.Y.Z`
   - `git push origin addon-vX.Y.Z`
4. Wait for `Blender Addon Release` workflow.
5. Verify release assets include zip + checksum.

## Expected release assets

- `cinematic_astro_sim_blender_addon-vX.Y.Z.zip`
- `cinematic_astro_sim_blender_addon-vX.Y.Z.zip.sha256`

These are the only addon release deliverables; users can install the zip directly in Blender.
