from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SyncStatus:
    plugins_updated: int
    models_updated: int
    offline_cache: bool


class RegistrySyncService:
    def __init__(self) -> None:
        self._last = SyncStatus(0, 0, True)

    def sync(self, plugin_diff: int, model_diff: int, offline_cache: bool) -> SyncStatus:
        self._last = SyncStatus(plugin_diff, model_diff, offline_cache)
        return self._last

    def health(self) -> dict[str, str]:
        return {"status": "ok", "service": "registry_sync"}
