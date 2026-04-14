from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from sim_core.app import create_runtime  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Print compiled SimulationSpec as JSON")
    parser.add_argument("preset_id", help="Preset ID")
    args = parser.parse_args()

    runtime = create_runtime("warp")
    spec = runtime.compile_spec(args.preset_id)
    print(json.dumps(asdict(spec), indent=2))


if __name__ == "__main__":
    main()
