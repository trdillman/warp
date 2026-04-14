from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from sim_core.app import create_runtime
from sim_core.cache_io import read_snapshot
from sim_core.contracts import SIMULATION_SPEC_VERSION, SimulationRunRequest


class TestVerticalSlice(unittest.TestCase):
    def test_runtime_compiles_and_runs_moon_birth_spec(self):
        runtime = create_runtime("warp")
        spec = runtime.compile_spec("moon_birth_theia")

        self.assertEqual(spec.spec_version, SIMULATION_SPEC_VERSION)
        self.assertEqual(spec.preset_id, "moon_birth_theia")
        self.assertGreater(len(spec.particle_init.positions), 0)

        with tempfile.TemporaryDirectory() as tmp:
            request = SimulationRunRequest(
                preset_id="moon_birth_theia",
                steps=6,
                dt=0.02,
                output_dir=tmp,
                save_every=2,
            )
            snapshots = runtime.run(request)

            self.assertEqual(len(snapshots), 3)
            for path in snapshots:
                self.assertTrue(path.exists())

            last_state = read_snapshot(Path(snapshots[-1]))
            self.assertEqual(last_state.frame, 6)
            self.assertEqual(len(last_state.positions), len(last_state.velocities))
            self.assertGreater(len(last_state.positions), 0)

            run_dirs = list((Path(tmp) / "runs").glob("*"))
            self.assertEqual(len(run_dirs), 1)
            self.assertTrue((run_dirs[0] / "run_manifest.json").exists())
            self.assertTrue((run_dirs[0] / "run_summary.txt").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
