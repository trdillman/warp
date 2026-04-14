from __future__ import annotations

import argparse
import ast
import hashlib
import os
import platform
import shutil
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import BadZipFile, ZIP_DEFLATED, ZipFile, ZipInfo

ADDON_NAME = "cinematic_astro_sim"
REPO_ROOT = Path(__file__).resolve().parents[1]
DIST_DIR = REPO_ROOT / "dist"
RUNTIME_CACHE_DIR = REPO_ROOT / ".runtime-cache"
ADDON_INIT = REPO_ROOT / "addon" / "__init__.py"

INCLUDE_DIRS = ["sim_core", "presets", "backends", "io"]
ADDON_FILES = ["__init__.py", "operators.py", "props.py", "ui.py", "cache_bridge.py", "visualization.py"]

WARP_RUNTIME_PACKAGE = "warp-lang"
WARP_RUNTIME_VERSION = "1.12.1"
WARP_RUNTIME_WHEEL = f"warp_lang-{WARP_RUNTIME_VERSION}-py3-none-win_amd64.whl"
WARP_RUNTIME_SHA256 = "826b2f93df8e47eac0c751a8eb5a0533e2fc5434158c8896a63be53bfbd728c7"
WARP_RUNTIME_ENV = "ASTROSIM_WARP_RUNTIME_WHEEL"


def _copytree(src: Path, dst: Path) -> None:
    shutil.copytree(
        src,
        dst,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"),
    )


def _is_valid_runtime_wheel(wheel_path: Path, *, require_hash: bool) -> bool:
    if not wheel_path.exists() or wheel_path.suffix != ".whl":
        return False

    if require_hash:
        digest = hashlib.sha256(wheel_path.read_bytes()).hexdigest()
        if digest != WARP_RUNTIME_SHA256:
            return False

    try:
        with ZipFile(wheel_path, "r") as wheel:
            return any(name.startswith("warp/bin/") and not name.endswith(".gitignore") for name in wheel.namelist())
    except BadZipFile:
        return False


def _download_runtime_wheel(cache_dir: Path) -> Path:
    if platform.system() != "Windows":
        raise RuntimeError(
            "Automatic runtime download is only supported on Windows hosts. "
            f"Set {WARP_RUNTIME_ENV} to a local {WARP_RUNTIME_WHEEL} path on other platforms."
        )

    cache_dir.mkdir(parents=True, exist_ok=True)
    destination = cache_dir / WARP_RUNTIME_WHEEL
    if _is_valid_runtime_wheel(destination, require_hash=True):
        return destination

    if destination.exists():
        destination.unlink()

    uv_executable = shutil.which("uv")
    if not uv_executable:
        raise RuntimeError("Could not find `uv` on PATH to download the pinned Warp runtime wheel.")

    command = [
        uv_executable,
        "tool",
        "run",
        "--from",
        "pip",
        "pip",
        "download",
        "--dest",
        str(cache_dir),
        "--only-binary=:all:",
        f"{WARP_RUNTIME_PACKAGE}=={WARP_RUNTIME_VERSION}",
    ]
    result = subprocess.run(command, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            "Failed to download the pinned Warp runtime wheel. "
            f"Set {WARP_RUNTIME_ENV} to a local wheel path to continue.\n{result.stderr.strip()}"
        )

    if not _is_valid_runtime_wheel(destination, require_hash=True):
        if destination.exists():
            destination.unlink()
        raise RuntimeError(
            "Downloaded Warp runtime wheel failed validation. "
            f"Expected {WARP_RUNTIME_WHEEL} with sha256 {WARP_RUNTIME_SHA256}."
        )

    return destination


def resolve_runtime_wheel(explicit_wheel: Path | None = None) -> Path:
    configured = explicit_wheel
    if configured is None:
        env_value = os.environ.get(WARP_RUNTIME_ENV)
        if env_value:
            configured = Path(env_value)

    if configured is not None:
        wheel_path = configured.expanduser().resolve()
        if not wheel_path.exists():
            raise RuntimeError(f"Configured Warp runtime wheel does not exist: {wheel_path}")
        if wheel_path.suffix != ".whl":
            raise RuntimeError(f"Configured Warp runtime must be a .whl file: {wheel_path}")
        if not _is_valid_runtime_wheel(wheel_path, require_hash=False):
            raise RuntimeError(f"Configured Warp runtime wheel failed validation: {wheel_path}")
        return wheel_path

    return _download_runtime_wheel(RUNTIME_CACHE_DIR)


def _bundle_runtime(addon_root: Path, runtime_wheel: Path) -> None:
    with ZipFile(runtime_wheel, "r") as wheel:
        members = [name for name in wheel.namelist() if name.startswith("warp/") and not name.endswith("/")]
        if not members:
            raise RuntimeError(f"Warp runtime wheel did not contain a packaged warp/ module: {runtime_wheel}")

        native_members = [name for name in members if name.startswith("warp/bin/") and not name.endswith(".gitignore")]
        if not native_members:
            raise RuntimeError(
                "Warp runtime wheel did not contain native runtime files under warp/bin/. "
                "The bundled addon release would not be self-contained."
            )

        for member in members:
            target = addon_root / member
            target.parent.mkdir(parents=True, exist_ok=True)
            with wheel.open(member, "r") as source, target.open("wb") as output:
                shutil.copyfileobj(source, output)


def build_staging_tree(staging_root: Path, runtime_wheel: Path | None = None) -> Path:
    addon_root = staging_root / ADDON_NAME
    addon_root.mkdir(parents=True, exist_ok=True)

    source_addon = REPO_ROOT / "addon"
    for filename in ADDON_FILES:
        shutil.copy2(source_addon / filename, addon_root / filename)

    for dirname in INCLUDE_DIRS:
        _copytree(REPO_ROOT / dirname, addon_root / dirname)

    _bundle_runtime(addon_root, resolve_runtime_wheel(runtime_wheel))
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

    zip_name = f"{ADDON_NAME}_blender_addon-v{version}-windows.zip"
    checksum_name = f"{zip_name}.sha256"
    return zip_name, checksum_name


def write_sha256(path: Path) -> Path:
    """Write sha256 checksum file adjacent to a build artifact."""

    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    checksum_path = path.with_name(f"{path.name}.sha256")
    checksum_path.write_text(f"{digest}  {path.name}\n", encoding="utf-8")
    return checksum_path


def build_addon_zip(
    output_path: Path | None = None,
    version: str | None = None,
    runtime_wheel: Path | None = None,
) -> tuple[Path, Path]:
    active_version = version or detect_addon_version()
    default_name, _ = build_release_filenames(active_version)
    artifact = output_path or DIST_DIR / default_name
    with TemporaryDirectory() as tmp:
        staging = Path(tmp)
        addon_root = build_staging_tree(staging, runtime_wheel=runtime_wheel)
        _write_deterministic_zip(addon_root, artifact)
    checksum = write_sha256(artifact)
    return artifact, checksum


def main() -> None:
    parser = argparse.ArgumentParser(description="Build an installable Windows Blender addon zip with a bundled Warp runtime")
    parser.add_argument("--output", type=Path, default=None, help="Optional output zip path")
    parser.add_argument("--runtime-wheel", type=Path, default=None, help="Optional local Warp runtime wheel override")
    parser.add_argument("--version", default=None, help="Optional version string for release naming")
    parser.add_argument("--print-version", action="store_true", help="Print addon bl_info version and exit")
    parser.add_argument(
        "--print-runtime-wheel",
        action="store_true",
        help="Print the resolved Warp runtime wheel path and exit",
    )
    args = parser.parse_args()

    if args.print_version:
        print(detect_addon_version())
        return

    if args.print_runtime_wheel:
        print(resolve_runtime_wheel(args.runtime_wheel))
        return

    artifact, checksum = build_addon_zip(args.output, version=args.version, runtime_wheel=args.runtime_wheel)
    print(f"Wrote addon zip: {artifact}")
    print(f"Wrote checksum: {checksum}")


if __name__ == "__main__":
    main()
