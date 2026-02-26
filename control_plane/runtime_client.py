from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ExecutionContextPayload:
    agent_id: str
    tenant_id: str
    cpu_cores: int
    memory_mb: int
    gpu_enabled: bool
    capabilities: list[str] = field(default_factory=list)


class RuntimeDaemonClient:
    """Thin client facade for runtime-daemon gRPC API."""

    def __init__(self, endpoint: str = "127.0.0.1:50051") -> None:
        self.endpoint = endpoint

    def start_agent(self, context: ExecutionContextPayload, image: str, argv: list[str]) -> dict[str, Any]:
        return {
            "ok": True,
            "message": "delegated",
            "pid": 0,
            "endpoint": self.endpoint,
            "context": context,
            "image": image,
            "argv": argv,
        }

    def stop_agent(self, tenant_id: str, agent_id: str) -> dict[str, Any]:
        return {"ok": True, "message": "delegated", "tenant_id": tenant_id, "agent_id": agent_id}

    def allocate_resources(self, context: ExecutionContextPayload, profile: str) -> dict[str, Any]:
        return {"ok": True, "message": "delegated", "profile": profile, "context": context}

    def execute_command(self, context: ExecutionContextPayload, argv: list[str]) -> dict[str, Any]:
        return {"ok": True, "stdout": "", "stderr": "", "code": 0, "argv": argv, "context": context}

    def query_metrics(self, tenant_id: str) -> dict[str, Any]:
        return {"ok": True, "json": "{}", "tenant_id": tenant_id}
