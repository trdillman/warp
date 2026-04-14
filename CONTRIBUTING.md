# Contributing

Keep contributions focused on the Blender addon, runtime contracts, packaging, tests, and addon-facing documentation.

## Development workflow

1. Create a feature branch.
2. Run the targeted unit tests for the area you changed.
3. If packaging changed, build a Windows addon zip locally.
4. Update docs when behavior or release flow changes.

## Minimum checks

```powershell
python -m unittest tests.test_repo_layout
python -m unittest tests.test_blender_packaging
python -m unittest tests.test_cache_visualization_prep
```

## Packaging note

Do not commit a vendored upstream `warp/` source tree back into this repository.
The release build bundles a pinned Windows Warp wheel at packaging time.
