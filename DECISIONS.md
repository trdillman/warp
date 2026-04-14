# DECISIONS

## D-001: Keep Blender thin

Blender code (`addon/`) is a shell that builds requests and calls `sim_core` entrypoints.

Reason: preserves headless execution and prevents UI-driven architecture drift.

## D-002: Presets are plugins, not mini-addons

Presets implement one shared `PresetPlugin` contract and register into one shared registry.

Reason: avoids per-preset bespoke plumbing and ensures coherent long-lived architecture.

## D-003: Backend boundary is explicit

Compute implementation is isolated behind `BackendAdapter`.

Reason: enables backend swaps/variants with clear contracts.

## D-004: File-backed state first

Snapshots and run metadata are explicit files (`cache_snapshot_v1`, `run_manifest_v1`).

Reason: restartability, inspectability, and continuation safety.

## D-005: SimulationSpec is the neutral IR

All presets now compile into `SimulationSpec`, and runtime executes specs rather than preset-owned runtime logic.

Reason: keeps architecture stable and preserves future node-graph compatibility.

## D-006: No backend imports in addon or presets

`addon/` and `presets/` must not import from `backends/`.

Reason: protects boundary clarity and prevents architectural leakage.
