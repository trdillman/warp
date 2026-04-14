from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from sim_core.cache_io import read_snapshot  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect a cache snapshot JSON")
    parser.add_argument("snapshot", type=Path, help="Path to frame_XXXXX.json")
    args = parser.parse_args()

    snapshot = read_snapshot(args.snapshot)
    print(f"schema_version={snapshot.schema_version}")
    print(f"frame={snapshot.frame}")
    print(f"time={snapshot.time}")
    print(f"particle_count={len(snapshot.positions)}")
    print(f"materials={sorted(set(snapshot.materials))}")


if __name__ == "__main__":
    main()
