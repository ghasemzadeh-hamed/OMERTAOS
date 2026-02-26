from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AgentCreated:
    agent_id: str
    tenant_id: str
