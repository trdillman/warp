from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from sim_core.app import create_runtime  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a preset compiles into SimulationSpec")
    parser.add_argument("preset_id", help="Preset ID to validate")
    args = parser.parse_args()

    runtime = create_runtime("warp")
    spec = runtime.compile_spec(args.preset_id)
    particle_count = len(spec.particle_init.positions)
    if particle_count == 0:
        raise ValueError(f"Preset {args.preset_id} compiled to zero particles")

    print(f"Preset '{args.preset_id}' is valid")
    print(f"spec_version={spec.spec_version}")
    print(f"particles={particle_count}")


if __name__ == "__main__":
    main()
