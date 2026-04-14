# AGENTS.md

## Repo focus

This repository is a Blender addon project, not a general-purpose Warp source tree.
Keep changes scoped to the addon, its runtime contracts, packaging, tests, and addon-facing docs.

## Working rules

- Prefer `uv run` for project commands.
- Do not reintroduce a vendored upstream `warp/` source checkout.
- Treat `scripts/build_blender_addon_zip.py` as the source of truth for release packaging.
- Windows release artifacts must bundle a pinned Warp runtime wheel.
- Keep docs addon-specific; remove or rewrite any upstream Warp guidance instead of layering on exceptions.

## Verification

- Repo shape: `python -m unittest tests.test_repo_layout`
- Packaging: `python -m unittest tests.test_blender_packaging`
- Cache/display prep: `python -m unittest tests.test_cache_visualization_prep`
- Local release smoke test: `uv run scripts/build_blender_addon_zip.py`

## Release notes

- Version source of truth is `ADDON_VERSION` / `bl_info["version"]` in `addon/__init__.py`.
- Release tags use `addon-vX.Y.Z`.
- The published zip is Windows-only and should include the bundled `warp/` runtime files.
