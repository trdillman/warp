from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from sim_core.app import create_runtime
from sim_core.contracts import SimulationRunRequest


class TestSettlingAndResume(unittest.TestCase):
    def test_resume_from_cache_snapshot(self):
        runtime = create_runtime("warp")
        with tempfile.TemporaryDirectory() as tmp:
            first = SimulationRunRequest(
                preset_id="moon_birth_theia",
                steps=6,
                dt=0.008,
                output_dir=tmp,
                save_every=3,
            )
            snapshots = runtime.run(first)
            self.assertEqual(len(snapshots), 2)

            second = SimulationRunRequest(
                preset_id="moon_birth_theia",
                steps=3,
                dt=0.008,
                output_dir=tmp,
                save_every=3,
                resume_snapshot=str(snapshots[-1]),
            )
            resumed = runtime.run(second)
            self.assertEqual(len(resumed), 1)
            self.assertTrue(Path(resumed[0]).exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
