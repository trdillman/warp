from __future__ import annotations

import json
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
            "densities": [1.0],
            "internal_energy": [0.0],
            "smoothing_lengths": [0.1],
            "material_ids": [0],
            "provenance_ids": [0],
        }
        validate_snapshot_payload(payload)

        bad = dict(payload)
        bad["schema_version"] = "old"
        with self.assertRaises(CacheValidationError):
            validate_snapshot_payload(bad)

    def test_diagnostics_artifact_written(self):
        runtime = create_runtime("warp")
        with tempfile.TemporaryDirectory() as tmp:
            request = SimulationRunRequest(
                preset_id="moon_birth_theia",
                steps=8,
                dt=0.008,
                output_dir=tmp,
                save_every=4,
            )
            runtime.run(request)
            diagnostics_files = sorted((Path(tmp) / "diagnostics").glob("*.json"))
            self.assertGreater(len(diagnostics_files), 0)
            data = json.loads(diagnostics_files[-1].read_text(encoding="utf-8"))
            self.assertIn("bound_circumterrestrial_mass", data)
            self.assertIn("escaping_mass", data)


if __name__ == "__main__":
    unittest.main(verbosity=2)
