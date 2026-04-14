from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from presets import build_default_registry
from sim_core.app import create_runtime
from sim_core.cache_io import CacheValidationError, validate_snapshot_payload
from sim_core.contracts import CACHE_SCHEMA_VERSION, SIMULATION_SPEC_VERSION, SimulationRunRequest


class TestArchitectureGuardrails(unittest.TestCase):
    def test_preset_modules_do_not_import_backend_or_warp(self):
        for file in Path("presets").glob("*.py"):
            if file.name == "__init__.py":
                continue
            text = file.read_text(encoding="utf-8")
            self.assertNotIn("import warp", text, msg=f"Preset leaks Warp import: {file}")
            self.assertNotIn("from backends", text, msg=f"Preset leaks backend import: {file}")

    def test_addon_modules_do_not_import_backends(self):
        for file in Path("addon").glob("*.py"):
            text = file.read_text(encoding="utf-8")
            self.assertNotIn("from backends", text, msg=f"Addon leaks backend import: {file}")

    def test_all_presets_compile_to_simulation_spec(self):
        runtime = create_runtime("warp")
        registry = build_default_registry()
        for plugin in registry.all():
            spec = runtime.compile_spec(plugin.meta.preset_id)
            self.assertEqual(spec.spec_version, SIMULATION_SPEC_VERSION)
            self.assertEqual(spec.preset_id, plugin.meta.preset_id)
            self.assertGreater(len(spec.particle_init.positions), 0)

    def test_cache_payload_requires_schema_version(self):
        payload = {
            "schema_version": CACHE_SCHEMA_VERSION,
            "frame": 0,
            "time": 0.0,
            "positions": [[0.0, 0.0, 0.0]],
            "velocities": [[0.0, 0.0, 0.0]],
            "masses": [1.0],
            "materials": ["m"],
        }
        validate_snapshot_payload(payload)

        payload_bad = dict(payload)
        payload_bad["schema_version"] = "old"
        with self.assertRaises(CacheValidationError):
            validate_snapshot_payload(payload_bad)

    def test_second_preset_runs_through_same_runtime_path(self):
        runtime = create_runtime("warp")
        with tempfile.TemporaryDirectory() as tmp:
            request = SimulationRunRequest(
                preset_id="asteroid_belt_disruption",
                steps=4,
                dt=0.02,
                output_dir=tmp,
                save_every=2,
            )
            snapshots = runtime.run(request)
            self.assertEqual(len(snapshots), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
