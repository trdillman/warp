from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from sim_core.cache_io import read_snapshot, write_snapshot
from sim_core.contracts import BackendAdapter, PresetConfig, SimulationRunRequest, SimulationSpec
from sim_core.diagnostics import classify_debris, write_diagnostics
from sim_core.observability import write_run_manifest, write_run_summary
from sim_core.registry import PresetRegistry


class SimulationRuntime:
    """Shared simulation orchestration independent of Blender."""

    def __init__(self, registry: PresetRegistry, backend: BackendAdapter):
        self.registry = registry
        self.backend = backend

    def compile_spec(self, preset_id: str, config: PresetConfig | None = None) -> SimulationSpec:
        plugin = self.registry.get(preset_id)
        active_config = config or plugin.default_config()
        return plugin.compile_spec(active_config)

    def _choose_dt(self, spec: SimulationSpec, step_stats: dict[str, float]) -> tuple[float, str]:
        rt = spec.runtime
        cfl_dt = rt.cfl_factor * step_stats.get("cfl_dt", rt.dt)
        accel_dt = rt.accel_factor * step_stats.get("accel_dt", rt.dt)
        disp_dt = rt.displacement_factor * step_stats.get("disp_dt", rt.dt)

        dt_candidates = {
            "cfl": cfl_dt,
            "accel": accel_dt,
            "displacement": disp_dt,
            "max": rt.dt_max,
        }
        limiter = min(dt_candidates, key=dt_candidates.get)
        dt = max(rt.dt_min, min(rt.dt_max, dt_candidates[limiter]))
        return dt, limiter

    def run(self, request: SimulationRunRequest, config: PresetConfig | None = None) -> list[Path]:
        spec = self.compile_spec(request.preset_id, config=config)

        dt = request.dt if request.dt is not None else spec.runtime.dt
        steps = request.steps if request.steps is not None else spec.runtime.default_steps
        save_every = request.save_every if request.save_every is not None else spec.cache_settings.save_every

        if dt <= 0 or steps <= 0 or save_every <= 0:
            raise ValueError("Invalid run request values: dt/steps/save_every must be > 0")

        if request.resume_snapshot:
            resume_state = read_snapshot(Path(request.resume_snapshot))
            runtime_state = self.backend.initialize_from_state(spec, resume_state)
            start_frame = resume_state.frame
            start_time = resume_state.time
        else:
            runtime_state = self.backend.initialize(spec)
            self.backend.settle(runtime_state, spec)
            start_frame = 0
            start_time = 0.0

        output_dir = Path(request.output_dir)
        run_dir = output_dir / "runs" / datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")

        manifest = {
            "manifest_version": "run_manifest_v2",
            "preset_id": spec.preset_id,
            "spec_version": spec.spec_version,
            "backend": self.backend.name,
            "steps": steps,
            "initial_dt": dt,
            "output_dir": str(output_dir),
            "save_every": save_every,
            "solver_config": spec.solver_config,
            "eos_config": spec.eos_config,
            "runtime": {
                "dt_min": spec.runtime.dt_min,
                "dt_max": spec.runtime.dt_max,
                "cfl_factor": spec.runtime.cfl_factor,
                "accel_factor": spec.runtime.accel_factor,
                "displacement_factor": spec.runtime.displacement_factor,
            },
            "settling": spec.settle_config,
            "resume_snapshot": request.resume_snapshot,
        }
        write_run_manifest(run_dir / "run_manifest.json", manifest)

        snapshots: list[Path] = []
        limiter_counts: dict[str, int] = {}
        current_time = start_time

        for local_step in range(1, steps + 1):
            frame = start_frame + local_step
            step_stats = self.backend.step(runtime_state, dt)
            dt, limiter = self._choose_dt(spec, step_stats)
            limiter_counts[limiter] = limiter_counts.get(limiter, 0) + 1
            current_time += dt

            if frame % save_every == 0:
                snapshot = self.backend.snapshot(runtime_state, frame=frame, time=current_time)
                snapshot_path = output_dir / "cache" / f"frame_{frame:05d}.json"
                write_snapshot(snapshot_path, snapshot)
                snapshots.append(snapshot_path)

                if local_step % max(1, spec.cache_settings.diagnostics_every) == 0:
                    diagnostics = classify_debris(snapshot, spec)
                    diagnostics["frame"] = frame
                    diagnostics["time"] = current_time
                    diagnostics["dt_limiter_counts"] = limiter_counts
                    write_diagnostics(output_dir / "diagnostics" / f"frame_{frame:05d}.json", diagnostics)

        write_run_summary(
            run_dir / "run_summary.txt",
            preset_id=spec.preset_id,
            backend=self.backend.name,
            steps=steps,
            dt=dt,
            snapshots=len(snapshots),
        )

        diagnostics_path = output_dir / "diagnostics" / f"frame_{start_frame + steps:05d}.json"
        if diagnostics_path.exists():
            manifest["final_diagnostics"] = str(diagnostics_path)
            manifest["dt_limiter_counts"] = limiter_counts
            write_run_manifest(run_dir / "run_manifest.json", manifest)

        return snapshots
