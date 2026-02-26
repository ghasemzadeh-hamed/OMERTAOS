from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Capability:
    name: str
    scope: str


@dataclass(frozen=True, slots=True)
class Identity:
    agent_id: str
    tenant_id: str
    node_id: str
