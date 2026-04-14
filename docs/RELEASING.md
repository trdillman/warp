# Releasing the Blender Addon

This repository publishes a Windows Blender addon zip with a bundled Warp runtime.

## Version source of truth

Release version is `ADDON_VERSION` / `bl_info["version"]` in `addon/__init__.py`.

- Example: `(0, 2, 0)` -> `0.2.0`
- Release tags must match this version.

## Build locally

```powershell
uv run scripts/build_blender_addon_zip.py
```

Outputs:

- `dist/cinematic_astro_sim_blender_addon-vX.Y.Z-windows.zip`
- `dist/cinematic_astro_sim_blender_addon-vX.Y.Z-windows.zip.sha256`

Optional:

```powershell
uv run scripts/build_blender_addon_zip.py --print-version
uv run scripts/build_blender_addon_zip.py --print-runtime-wheel
uv run scripts/build_blender_addon_zip.py --runtime-wheel C:\path\to\warp_lang-1.12.1-py3-none-win_amd64.whl
```

## Runtime source

- Default behavior downloads the pinned `warp-lang` Windows wheel declared in `scripts/build_blender_addon_zip.py`.
- For offline or pre-fetched builds, set `ASTROSIM_WARP_RUNTIME_WHEEL` or pass `--runtime-wheel`.
- The release build must fail if the wheel cannot be resolved or if it does not contain native files under `warp/bin/`.

## Tag format

Use addon tags:

- `addon-vX.Y.Z`

Example:

- `addon-v0.2.0`

On tagged pushes, CI validates tag/version parity before publishing assets.

## GitHub Actions workflow

- Workflow: `.github/workflows/blender-addon-release.yml`
- Runner: Windows
- Triggers:
  - `workflow_dispatch`
  - push tag matching `addon-v*`

Behavior:

1. Resolve version from `addon/__init__.py`.
2. Resolve or download the pinned Windows runtime wheel.
3. Build the addon zip and checksum.
4. Upload workflow artifacts.
5. On tag pushes, publish a GitHub Release with both assets.
