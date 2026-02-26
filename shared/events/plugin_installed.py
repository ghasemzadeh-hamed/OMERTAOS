from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PluginInstalled:
    plugin_name: str
    tenant_id: str
