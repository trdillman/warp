from __future__ import annotations

from backends.warp import WarpBackendAdapter
from presets import build_default_registry
from sim_core.contracts import PresetConfig, SimulationRunRequest
from sim_core.runtime import SimulationRuntime


def create_runtime(backend_name: str = "warp") -> SimulationRuntime:
    """Create runtime instance using supported backend adapter."""

    if backend_name != "warp":
        raise ValueError(f"Unsupported backend '{backend_name}'. Supported: warp")

    return SimulationRuntime(registry=build_default_registry(), backend=WarpBackendAdapter())


def run_preset(request: SimulationRunRequest, config: PresetConfig | None = None) -> list[str]:
    """Execute a preset through the shared runtime path."""

    runtime = create_runtime("warp")
    return [str(path) for path in runtime.run(request, config=config)]
