"""In-memory registry of deployed agent instances."""
from __future__ import annotations

import asyncio
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class AgentInstance:
    id: str
    template_id: str
    tenant_id: str
    name: str
    config: Dict[str, Any]
    scope: str = "tenant"
    status: str = "draft"
    enabled: bool = True
    created_at: float = field(default_factory=lambda: time.time())
    updated_at: float = field(default_factory=lambda: time.time())


class AgentRegistry:
    """Lightweight agent registry placeholder until backed by persistent storage."""

    def __init__(self) -> None:
        self._agents: Dict[str, Dict[str, AgentInstance]] = {}
        self._lock = asyncio.Lock()

    async def list(self, tenant_id: str) -> List[AgentInstance]:
        async with self._lock:
            return list(self._agents.get(tenant_id, {}).values())

    async def get(self, tenant_id: str, agent_id: str) -> Optional[AgentInstance]:
        async with self._lock:
            return self._agents.get(tenant_id, {}).get(agent_id)

    async def create(
        self,
        tenant_id: str,
        template_id: str,
        name: str,
        config: Dict[str, Any],
        scope: str = "tenant",
        enabled: bool = True,
    ) -> AgentInstance:
        async with self._lock:
            agent_id = str(uuid.uuid4())
            instance = AgentInstance(
                id=agent_id,
                template_id=template_id,
                tenant_id=tenant_id,
                name=name,
                config=config,
                scope=scope,
                status="draft",
                enabled=enabled,
            )
            self._agents.setdefault(tenant_id, {})[agent_id] = instance
            return instance

    async def update(
        self,
        tenant_id: str,
        agent_id: str,
        *,
        name: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        status: Optional[str] = None,
        enabled: Optional[bool] = None,
    ) -> Optional[AgentInstance]:
        async with self._lock:
            instance = self._agents.get(tenant_id, {}).get(agent_id)
            if instance is None:
                return None
            if name is not None:
                instance.name = name
            if config is not None:
                instance.config = config
            if status is not None:
                instance.status = status
            if enabled is not None:
                instance.enabled = enabled
            instance.updated_at = time.time()
            return instance
