from __future__ import annotations

import random
import unittest

from sim_core.contracts import BodyInitConfig
from sim_core.initial_conditions import build_differentiated_body_particles


class TestInitialConditions(unittest.TestCase):
    def test_differentiated_body_builder_tracks_material_and_provenance(self):
        body = BodyInitConfig(
            body_id="earth",
            particle_count=100,
            radius=1.0,
            core_fraction=0.3,
            core_density=1.8,
            mantle_density=1.0,
            position=[0.0, 0.0, 0.0],
            velocity=[0.0, 0.0, 0.0],
            spin=[0.0, 0.0, 0.0],
            core_material_id=1,
            mantle_material_id=0,
            core_provenance_id=1,
            mantle_provenance_id=0,
        )
        init = build_differentiated_body_particles(body, random.Random(5), base_h=0.1)
        self.assertEqual(len(init.positions), 100)
        self.assertEqual(len(init.material_ids), 100)
        self.assertEqual(len(init.provenance_ids), 100)
        self.assertIn(0, init.material_ids)
        self.assertIn(1, init.material_ids)


if __name__ == "__main__":
    unittest.main(verbosity=2)
