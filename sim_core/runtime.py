from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from sim_core.cache_io import write_snapshot
from sim_core.contracts import BackendAdapter, PresetConfig, SimulationRunRequest, SimulationSpec
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

    def run(self, request: SimulationRunRequest, config: PresetConfig | None = None) -> list[Path]:
        spec = self.compile_spec(request.preset_id, config=config)

        dt = request.dt if request.dt is not None else spec.runtime.dt
        steps = request.steps if request.steps is not None else spec.runtime.default_steps
        save_every = request.save_every if request.save_every is not None else spec.cache_settings.save_every

        if dt <= 0:
            raise ValueError(f"Invalid dt={dt}. dt must be > 0.")
        if steps <= 0:
            raise ValueError(f"Invalid steps={steps}. steps must be > 0.")
        if save_every <= 0:
            raise ValueError(f"Invalid save_every={save_every}. save_every must be > 0.")

        runtime_state = self.backend.initialize(spec)

        output_dir = Path(request.output_dir)
        run_dir = output_dir / "runs" / datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")

        manifest = {
            "manifest_version": "run_manifest_v1",
            "preset_id": spec.preset_id,
            "spec_version": spec.spec_version,
            "backend": self.backend.name,
            "steps": steps,
            "dt": dt,
            "output_dir": str(output_dir),
            "save_every": save_every,
            "solver_config": spec.solver_config,
            "backend_requirements": {
                "backend": spec.backend_requirements.backend,
                "min_precision": spec.backend_requirements.min_precision,
                "features": list(spec.backend_requirements.features),
            },
            "cache_settings": {
                "cache_format": spec.cache_settings.cache_format,
                "include_velocity": spec.cache_settings.include_velocity,
            },
        }
        write_run_manifest(run_dir / "run_manifest.json", manifest)

        snapshots: list[Path] = []
        for frame in range(1, steps + 1):
            self.backend.step(runtime_state, dt)
            if frame % save_every == 0:
                snapshot = self.backend.snapshot(runtime_state, frame=frame, time=frame * dt)
                snapshot_path = output_dir / "cache" / f"frame_{frame:05d}.json"
                write_snapshot(snapshot_path, snapshot)
                snapshots.append(snapshot_path)

        write_run_summary(
            run_dir / "run_summary.txt",
            preset_id=spec.preset_id,
            backend=self.backend.name,
            steps=steps,
            dt=dt,
            snapshots=len(snapshots),
        )
        return snapshots
