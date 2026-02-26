from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RuntimeEnvelope:
    tenant_id: str
    agent_id: str
    argv: list[str]


class RuntimeDaemonClient:
    def __init__(self, endpoint: str = "unix:///run/omertaos/runtime.sock") -> None:
        self.endpoint = endpoint

    async def execute(self, envelope: RuntimeEnvelope) -> dict[str, object]:
        return {
            "ok": True,
            "endpoint": self.endpoint,
            "tenant_id": envelope.tenant_id,
            "agent_id": envelope.agent_id,
            "argv": envelope.argv,
        }
