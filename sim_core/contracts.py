from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

SIMULATION_SPEC_VERSION = "sim_spec_v1"
CACHE_SCHEMA_VERSION = "cache_snapshot_v1"


@dataclass(frozen=True)
class PresetMeta:
    """User-facing preset metadata and authoring hints."""

    preset_id: str
    display_name: str
    description: str
    tags: tuple[str, ...] = ()
    category: str = "cinematic"
    contract_version: str = "preset_v1"


@dataclass
class PresetConfig:
    """Preset configuration values for a simulation run."""

    values: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RuntimeSettings:
    """Settings controlling runtime stepping behavior."""

    dt: float
    default_steps: int


@dataclass(frozen=True)
class BackendRequirements:
    """Backend requirements declared by a preset specification."""

    backend: str = "warp"
    min_precision: str = "float32"
    features: tuple[str, ...] = ()


@dataclass(frozen=True)
class CacheSettings:
    """Cache/output settings declared in a simulation specification."""

    save_every: int = 1
    cache_format: str = "json"
    include_velocity: bool = True


@dataclass(frozen=True)
class VisualizationHints:
    """Optional visualization hints for Blender and offline tools."""

    point_radius: float = 0.1
    color_mode: str = "material"


@dataclass
class MaterialDef:
    """Simple material reference object used by particle initialization."""

    material_id: str
    display_name: str


@dataclass
class ParticleInit:
    """Particle initialization payload in backend-agnostic form."""

    positions: list[list[float]]
    velocities: list[list[float]]
    masses: list[float]
    materials: list[str]


@dataclass
class SimulationSpec:
    """Backend-agnostic intermediate representation for simulation execution."""

    spec_version: str
    preset_id: str
    particle_init: ParticleInit
    materials: list[MaterialDef]
    solver_config: dict[str, Any]
    runtime: RuntimeSettings
    backend_requirements: BackendRequirements
    cache_settings: CacheSettings
    visualization_hints: VisualizationHints
    parameter_defaults: dict[str, Any] = field(default_factory=dict)


@dataclass
class SimulationState:
    """Serializable simulation state passed across layers and cache files."""

    schema_version: str
    frame: int
    time: float
    positions: list[list[float]]
    velocities: list[list[float]]
    masses: list[float]
    materials: list[str]


@dataclass
class SimulationRunRequest:
    """Requested execution settings for a simulation run."""

    preset_id: str
    steps: int | None = None
    dt: float | None = None
    output_dir: str = "/tmp/astrosim"
    save_every: int | None = None


class BackendAdapter(Protocol):
    """Backend contract implemented by compute backends (for example Warp)."""

    name: str

    def initialize(self, spec: SimulationSpec) -> Any:
        """Return backend-owned runtime buffers from a backend-agnostic spec."""

    def step(self, runtime_state: Any, dt: float) -> None:
        """Advance runtime state by one step."""

    def snapshot(self, runtime_state: Any, frame: int, time: float) -> SimulationState:
        """Return a serializable snapshot from backend runtime buffers."""


class PresetPlugin(Protocol):
    """Versioned preset contract used by Blender and headless runtime."""

    meta: PresetMeta

    def default_config(self) -> PresetConfig:
        """Return default values for UI and headless callers."""

    def compile_spec(self, config: PresetConfig) -> SimulationSpec:
        """Compile preset configuration into a backend-agnostic SimulationSpec."""
