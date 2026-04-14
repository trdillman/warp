from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from scripts.build_blender_addon_zip import ADDON_NAME, build_addon_zip, build_staging_tree, resolve_runtime_wheel


def _build_fake_runtime_wheel(path: Path) -> Path:
    with ZipFile(path, "w") as zf:
        zf.writestr("warp/__init__.py", "__version__ = 'test'\n")
        zf.writestr("warp/config.py", "mode = 'test'\n")
        zf.writestr("warp/bin/warp.dll", b"fake-binary")
    return path


class TestBlenderPackaging(unittest.TestCase):
    def test_build_addon_zip_contains_expected_modules_and_runtime(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            artifact = tmp_path / "addon.zip"
            runtime_wheel = _build_fake_runtime_wheel(tmp_path / "warp_lang-test.whl")

            _, checksum = build_addon_zip(artifact, runtime_wheel=runtime_wheel)
            self.assertTrue(artifact.exists())
            self.assertTrue(checksum.exists())

            with ZipFile(artifact, "r") as zf:
                names = set(zf.namelist())

            expected = {
                f"{ADDON_NAME}/__init__.py",
                f"{ADDON_NAME}/operators.py",
                f"{ADDON_NAME}/sim_core/contracts.py",
                f"{ADDON_NAME}/presets/moon_birth_theia.py",
                f"{ADDON_NAME}/backends/warp/adapter.py",
                f"{ADDON_NAME}/io/cache_schema_v1.json",
                f"{ADDON_NAME}/warp/__init__.py",
                f"{ADDON_NAME}/warp/config.py",
                f"{ADDON_NAME}/warp/bin/warp.dll",
            }
            self.assertTrue(expected.issubset(names))

    def test_build_staging_tree_rejects_runtime_without_native_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            runtime_wheel = tmp_path / "warp_lang-bad.whl"
            with ZipFile(runtime_wheel, "w") as zf:
                zf.writestr("warp/__init__.py", "__version__ = 'test'\n")

            with self.assertRaisesRegex(RuntimeError, "failed validation"):
                build_staging_tree(tmp_path / "staging", runtime_wheel=runtime_wheel)

    def test_resolve_runtime_wheel_reports_missing_override(self):
        missing = Path(tempfile.gettempdir()) / "does-not-exist.whl"
        with self.assertRaisesRegex(RuntimeError, "does not exist"):
            resolve_runtime_wheel(missing)


if __name__ == "__main__":
    unittest.main(verbosity=2)
