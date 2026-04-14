from presets.asteroid_belt_disruption import AsteroidBeltDisruptionPreset
from presets.moon_birth_theia import MoonBirthTheiaPreset
from sim_core.contracts import PresetMeta
from sim_core.registry import PresetRegistry


def build_default_registry() -> PresetRegistry:
    registry = PresetRegistry()
    registry.register(MoonBirthTheiaPreset())
    registry.register(AsteroidBeltDisruptionPreset())
    return registry


def list_preset_metadata() -> list[PresetMeta]:
    return [plugin.meta for plugin in build_default_registry().all()]
