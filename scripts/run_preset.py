from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from sim_core.app import create_runtime  # noqa: E402
from sim_core.contracts import PresetConfig, SimulationRunRequest  # noqa: E402


def parse_overrides(override_args: list[str]) -> dict:
    values: dict = {}
    for pair in override_args:
        key, raw = pair.split("=", 1)
        try:
            values[key] = json.loads(raw)
        except json.JSONDecodeError:
            values[key] = raw
    return values


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a cinematic astrophysical preset headlessly")
    parser.add_argument("--preset-id", default="moon_birth_theia", help="Preset ID to run")
    parser.add_argument("--steps", type=int, default=None, help="Number of simulation steps")
    parser.add_argument("--dt", type=float, default=None, help="Simulation timestep")
    parser.add_argument("--output-dir", default="/tmp/astrosim", help="Output directory")
    parser.add_argument("--save-every", type=int, default=None, help="Snapshot cadence")
    parser.add_argument("--resume-snapshot", default=None, help="Resume from snapshot JSON")
    parser.add_argument(
        "--override", action="append", default=[], help="Preset config override key=value (JSON parsed)"
    )
    parser.add_argument("--print-spec", action="store_true", help="Print compiled SimulationSpec metadata")
    args = parser.parse_args()

    runtime = create_runtime("warp")

    config = None
    if args.override:
        config = PresetConfig(values=parse_overrides(args.override))

    if args.print_spec:
        spec = runtime.compile_spec(args.preset_id, config=config)
        print(f"spec_version={spec.spec_version}")
        print(f"preset_id={spec.preset_id}")
        print(f"particles={len(spec.particle_init.positions)}")
        print(f"solver_mode={spec.solver_config.get('mode')}")
        print(f"settling={spec.settle_config}")

    request = SimulationRunRequest(
        preset_id=args.preset_id,
        steps=args.steps,
        dt=args.dt,
        output_dir=args.output_dir,
        save_every=args.save_every,
        resume_snapshot=args.resume_snapshot,
    )
    snapshots = runtime.run(request, config=config)

    print(f"Wrote {len(snapshots)} snapshots to {args.output_dir}/cache")
    if snapshots:
        print(f"Last snapshot: {snapshots[-1]}")


if __name__ == "__main__":
    main()
