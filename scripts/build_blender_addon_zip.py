from __future__ import annotations

import argparse
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ADDON_NAME = "cinematic_astro_sim"
REPO_ROOT = Path(__file__).resolve().parents[1]
DIST_DIR = REPO_ROOT / "dist"

INCLUDE_DIRS = ["sim_core", "presets", "backends", "io"]
ADDON_FILES = ["__init__.py", "operators.py", "props.py", "ui.py", "cache_bridge.py", "visualization.py"]


def _copytree(src: Path, dst: Path) -> None:
    shutil.copytree(
        src,
        dst,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store", "*.so", "*.pyd"),
    )


def build_staging_tree(staging_root: Path) -> Path:
    addon_root = staging_root / ADDON_NAME
    addon_root.mkdir(parents=True, exist_ok=True)

    source_addon = REPO_ROOT / "addon"
    for filename in ADDON_FILES:
        shutil.copy2(source_addon / filename, addon_root / filename)

    for dirname in INCLUDE_DIRS:
        _copytree(REPO_ROOT / dirname, addon_root / dirname)

    return addon_root


def _write_deterministic_zip(source_dir: Path, output_zip: Path) -> None:
    output_zip.parent.mkdir(parents=True, exist_ok=True)
    fixed_time = (2020, 1, 1, 0, 0, 0)

    with ZipFile(output_zip, "w", compression=ZIP_DEFLATED) as zf:
        for path in sorted(source_dir.rglob("*")):
            if path.is_dir():
                continue
            relative = path.relative_to(source_dir.parent).as_posix()
            info = ZipInfo(relative)
            info.date_time = fixed_time
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, path.read_bytes())


def build_addon_zip(output_path: Path | None = None) -> Path:
    artifact = output_path or DIST_DIR / f"{ADDON_NAME}_blender_addon.zip"
    with TemporaryDirectory() as tmp:
        staging = Path(tmp)
        addon_root = build_staging_tree(staging)
        _write_deterministic_zip(addon_root, artifact)
    return artifact


def main() -> None:
    parser = argparse.ArgumentParser(description="Build installable Blender addon zip artifact")
    parser.add_argument("--output", type=Path, default=None, help="Optional output zip path")
    args = parser.parse_args()

    artifact = build_addon_zip(args.output)
    print(f"Wrote addon zip: {artifact}")


if __name__ == "__main__":
    main()
