from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from addon.cache_bridge import build_preview_config, find_latest_snapshot, load_display_payload
from sim_core.cache_io import write_snapshot
from sim_core.contracts import CACHE_SCHEMA_VERSION, PresetConfig, SimulationState


class TestCacheVisualizationPrep(unittest.TestCase):
    def test_find_latest_snapshot_uses_highest_frame(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache_dir = Path(tmp)
            for frame in (5, 15, 10):
                state = SimulationState(
                    schema_version=CACHE_SCHEMA_VERSION,
                    frame=frame,
                    time=float(frame),
                    positions=[[0.0, 0.0, 0.0]],
                    velocities=[[0.0, 0.0, 0.0]],
                    masses=[1.0],
                    densities=[1.0],
                    internal_energy=[0.5],
                    smoothing_lengths=[0.2],
                    material_ids=[0],
                    provenance_ids=[1],
                )
                write_snapshot(cache_dir / f"frame_{frame:05d}.json", state)

            latest = find_latest_snapshot(cache_dir)
            self.assertEqual(latest.name, "frame_00015.json")

    def test_display_modes_emit_particle_colors(self):
        with tempfile.TemporaryDirectory() as tmp:
            snapshot = Path(tmp) / "frame_00001.json"
            state = SimulationState(
                schema_version=CACHE_SCHEMA_VERSION,
                frame=1,
                time=0.1,
                positions=[[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]],
                velocities=[[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]],
                masses=[1.0, 1.0],
                densities=[1.0, 3.0],
                internal_energy=[0.5, 0.5],
                smoothing_lengths=[0.2, 0.2],
                material_ids=[0, 1],
                provenance_ids=[1, 2],
            )
            write_snapshot(snapshot, state)

            for mode in ("provenance", "material", "density"):
                payload = load_display_payload(snapshot, mode)
                self.assertEqual(len(payload.positions), 2)
                self.assertEqual(len(payload.colors), 2)

    def test_preview_config_overrides_particle_counts(self):
        base = PresetConfig(values={"earth_particles": 160, "theia_particles": 96, "settle_steps": 18})
        preview = build_preview_config(base, preview_steps=30, preview_save_every=3)

        self.assertEqual(preview.values["earth_particles"], 64)
        self.assertEqual(preview.values["theia_particles"], 40)
        self.assertEqual(preview.values["settle_steps"], 6)
        self.assertEqual(preview.values["default_steps"], 30)
        self.assertEqual(preview.values["save_every"], 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
