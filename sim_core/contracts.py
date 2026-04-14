from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

SIMULATION_SPEC_VERSION = "sim_spec_v2"
CACHE_SCHEMA_VERSION = "cache_snapshot_v2"


@dataclass(frozen=True)
class PresetMeta:
    """User-facing preset metadata and authoring hints."""

    preset_id: str
    display_name: str
    description: str
    tags: tuple[str, ...] = ()
    category: str = "cinematic"
    contract_version: str = "preset_v2"


@dataclass
class PresetConfig:
    """Preset configuration values for a simulation run."""

    values: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RuntimeSettings:
    """Settings controlling runtime stepping behavior."""

    dt: float
    default_steps: int
    dt_min: float
    dt_max: float
    cfl_factor: float
    accel_factor: float
    displacement_factor: float


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
    diagnostics_every: int = 1


@dataclass(frozen=True)
class VisualizationHints:
    """Optional visualization hints for Blender and offline tools."""

    point_radius: float = 0.1
    color_mode: str = "provenance"


@dataclass
class MaterialDef:
    """Material definition including EOS parameters."""

    material_id: int
    name: str
    eos_model: str
    eos_params: dict[str, float]


@dataclass
class ProvenanceDef:
    """Source-body provenance definitions for diagnostics and visualization."""

    provenance_id: int
    name: str


@dataclass
class BodyInitConfig:
    """Initial condition body definition for differentiated spheroids."""

    body_id: str
    particle_count: int
    radius: float
    core_fraction: float
    core_density: float
    mantle_density: float
    position: list[float]
    velocity: list[float]
    spin: list[float]
    core_material_id: int
    mantle_material_id: int
    core_provenance_id: int
    mantle_provenance_id: int


@dataclass
class ParticleInit:
    """Particle initialization payload in backend-agnostic form."""

    positions: list[list[float]]
    velocities: list[list[float]]
    masses: list[float]
    material_ids: list[int]
    provenance_ids: list[int]
    smoothing_lengths: list[float]
    internal_energy: list[float]


@dataclass
class SimulationSpec:
    """Backend-agnostic intermediate representation for simulation execution."""

    spec_version: str
    preset_id: str
    body_configs: list[BodyInitConfig]
    particle_init: ParticleInit
    materials: list[MaterialDef]
    provenances: list[ProvenanceDef]
    eos_config: dict[str, Any]
    solver_config: dict[str, Any]
    runtime: RuntimeSettings
    backend_requirements: BackendRequirements
    cache_settings: CacheSettings
    visualization_hints: VisualizationHints
    diagnostics_config: dict[str, Any]
    settle_config: dict[str, Any]
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
    densities: list[float]
    internal_energy: list[float]
    smoothing_lengths: list[float]
    material_ids: list[int]
    provenance_ids: list[int]


@dataclass
class SimulationRunRequest:
    """Requested execution settings for a simulation run."""

    preset_id: str
    steps: int | None = None
    dt: float | None = None
    output_dir: str = "/tmp/astrosim"
    save_every: int | None = None
    resume_snapshot: str | None = None


class BackendAdapter(Protocol):
    """Backend contract implemented by compute backends (for example Warp)."""

    name: str

    def initialize(self, spec: SimulationSpec) -> Any:
        """Return backend-owned runtime buffers from a backend-agnostic spec."""

    def initialize_from_state(self, spec: SimulationSpec, state: SimulationState) -> Any:
        """Return backend-owned runtime buffers from a cached simulation state."""

    def settle(self, runtime_state: Any, spec: SimulationSpec) -> None:
        """Apply pre-impact settling/relaxation for initialized bodies."""

    def step(self, runtime_state: Any, dt: float) -> dict[str, float]:
        """Advance runtime state by one step and return step diagnostics."""

    def snapshot(self, runtime_state: Any, frame: int, time: float) -> SimulationState:
        """Return a serializable snapshot from backend runtime buffers."""


class PresetPlugin(Protocol):
    """Versioned preset contract used by Blender and headless runtime."""

    meta: PresetMeta

    def default_config(self) -> PresetConfig:
        """Return default values for UI and headless callers."""

    def compile_spec(self, config: PresetConfig) -> SimulationSpec:
        """Compile preset configuration into a backend-agnostic SimulationSpec."""
