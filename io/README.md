# IO Scaffold

This directory holds file-format contracts and helper scripts for cache/restart and exports.

Current contracts:

- Cache snapshots under `<output_dir>/cache/frame_XXXXX.json` using `cache_snapshot_v2`
- Structured run manifest under `<output_dir>/runs/<timestamp>/run_manifest.json`
- Human-readable summary under `<output_dir>/runs/<timestamp>/run_summary.txt`
- Diagnostics snapshots under `<output_dir>/diagnostics/frame_XXXXX.json`

Reference implementations:

- Snapshot reader/writer/validator: `sim_core/cache_io.py`
- Run manifest + summary writers: `sim_core/observability.py`
- Debris diagnostics: `sim_core/diagnostics.py`
- Inspector script: `scripts/inspect_cache.py`
