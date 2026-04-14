from __future__ import annotations

from dataclasses import dataclass, field

from sim_core.contracts import PresetPlugin


@dataclass
class PresetRegistry:
    """In-memory preset registry with explicit ID-based lookup."""

    _items: dict[str, PresetPlugin] = field(default_factory=dict)

    def register(self, plugin: PresetPlugin) -> None:
        preset_id = plugin.meta.preset_id
        if preset_id in self._items:
            raise ValueError(f"Preset already registered: {preset_id}")
        self._items[preset_id] = plugin

    def get(self, preset_id: str) -> PresetPlugin:
        try:
            return self._items[preset_id]
        except KeyError as err:
            known = ", ".join(sorted(self._items))
            raise KeyError(f"Unknown preset: {preset_id}. Known presets: {known}") from err

    def all(self) -> list[PresetPlugin]:
        return [self._items[key] for key in sorted(self._items)]

    def ids(self) -> list[str]:
        return sorted(self._items)
