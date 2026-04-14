from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from scripts.build_blender_addon_zip import ADDON_NAME, build_addon_zip


class TestBlenderPackaging(unittest.TestCase):
    def test_build_addon_zip_contains_expected_modules(self):
        with tempfile.TemporaryDirectory() as tmp:
            artifact = Path(tmp) / "addon.zip"
            build_addon_zip(artifact)
            self.assertTrue(artifact.exists())

            with ZipFile(artifact, "r") as zf:
                names = set(zf.namelist())

            expected = {
                f"{ADDON_NAME}/__init__.py",
                f"{ADDON_NAME}/operators.py",
                f"{ADDON_NAME}/sim_core/contracts.py",
                f"{ADDON_NAME}/presets/moon_birth_theia.py",
                f"{ADDON_NAME}/backends/warp/adapter.py",
                f"{ADDON_NAME}/io/cache_schema_v1.json",
            }
            self.assertTrue(expected.issubset(names))


if __name__ == "__main__":
    unittest.main(verbosity=2)
