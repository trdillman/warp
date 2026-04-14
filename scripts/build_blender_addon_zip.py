from __future__ import annotations

import argparse
import ast
import hashlib
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ADDON_NAME = "cinematic_astro_sim"
REPO_ROOT = Path(__file__).resolve().parents[1]
DIST_DIR = REPO_ROOT / "dist"
ADDON_INIT = REPO_ROOT / "addon" / "__init__.py"

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


def detect_addon_version() -> str:
    """Return addon version from ``addon/__init__.py`` bl_info."""

    source = ADDON_INIT.read_text(encoding="utf-8")
    module = ast.parse(source, filename=str(ADDON_INIT))
    addon_version: tuple[int, ...] | None = None

    for node in module.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "ADDON_VERSION":
                value = ast.literal_eval(node.value)
                if isinstance(value, tuple):
                    addon_version = tuple(int(part) for part in value)
                    return ".".join(str(part) for part in addon_version)

    for node in module.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "bl_info":
                if not isinstance(node.value, ast.Dict):
                    continue
                for key_node, value_node in zip(node.value.keys, node.value.values, strict=False):
                    if isinstance(key_node, ast.Constant) and key_node.value == "version":
                        version = ast.literal_eval(value_node)
                        if isinstance(version, tuple):
                            return ".".join(str(int(part)) for part in version)


    raise RuntimeError("Unable to read addon version from bl_info in addon/__init__.py")


def build_release_filenames(version: str) -> tuple[str, str]:
    """Return addon zip + checksum filenames for a release version."""

    zip_name = f"{ADDON_NAME}_blender_addon-v{version}.zip"
    checksum_name = f"{zip_name}.sha256"
    return zip_name, checksum_name


def write_sha256(path: Path) -> Path:
    """Write sha256 checksum file adjacent to a build artifact."""

    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    checksum_path = path.with_name(f"{path.name}.sha256")
    checksum_path.write_text(f"{digest}  {path.name}\n", encoding="utf-8")
    return checksum_path


def build_addon_zip(output_path: Path | None = None, version: str | None = None) -> tuple[Path, Path]:
    active_version = version or detect_addon_version()
    default_name, _ = build_release_filenames(active_version)
    artifact = output_path or DIST_DIR / default_name
    with TemporaryDirectory() as tmp:
        staging = Path(tmp)
        addon_root = build_staging_tree(staging)
        _write_deterministic_zip(addon_root, artifact)
    checksum = write_sha256(artifact)
    return artifact, checksum


def main() -> None:
    parser = argparse.ArgumentParser(description="Build installable Blender addon zip artifact")
    parser.add_argument("--output", type=Path, default=None, help="Optional output zip path")
    parser.add_argument("--version", default=None, help="Optional version string for release naming")
    parser.add_argument("--print-version", action="store_true", help="Print addon bl_info version and exit")
    args = parser.parse_args()

    if args.print_version:
        print(detect_addon_version())
        return

    artifact, checksum = build_addon_zip(args.output, version=args.version)
    print(f"Wrote addon zip: {artifact}")
    print(f"Wrote checksum: {checksum}")


if __name__ == "__main__":
    main()
