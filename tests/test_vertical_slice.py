from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from sim_core.app import create_runtime
from sim_core.cache_io import read_snapshot
from sim_core.contracts import CACHE_SCHEMA_VERSION, SIMULATION_SPEC_VERSION, SimulationRunRequest


class TestVerticalSlice(unittest.TestCase):
    def test_moon_birth_spec_and_run_outputs(self):
        runtime = create_runtime("warp")
        spec = runtime.compile_spec("moon_birth_theia")

        self.assertEqual(spec.spec_version, SIMULATION_SPEC_VERSION)
        self.assertEqual(spec.preset_id, "moon_birth_theia")
        self.assertEqual(spec.solver_config.get("mode"), "giant_impact_sph")
        self.assertGreater(len(spec.body_configs), 1)

        with tempfile.TemporaryDirectory() as tmp:
            request = SimulationRunRequest(
                preset_id="moon_birth_theia",
                steps=12,
                dt=0.008,
                output_dir=tmp,
                save_every=4,
            )
            snapshots = runtime.run(request)

            self.assertEqual(len(snapshots), 3)
            state = read_snapshot(Path(snapshots[-1]))
            self.assertEqual(state.schema_version, CACHE_SCHEMA_VERSION)
            self.assertEqual(len(state.positions), len(state.material_ids))
            self.assertEqual(len(state.positions), len(state.provenance_ids))
            self.assertGreater(max(state.densities), 0.0)

            diagnostics = sorted((Path(tmp) / "diagnostics").glob("*.json"))
            self.assertGreaterEqual(len(diagnostics), 1)

            run_dirs = list((Path(tmp) / "runs").glob("*"))
            self.assertEqual(len(run_dirs), 1)
            self.assertTrue((run_dirs[0] / "run_manifest.json").exists())
            self.assertTrue((run_dirs[0] / "run_summary.txt").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
