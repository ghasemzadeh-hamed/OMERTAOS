"""Linux kernel entrypoint for orchestration CI."""
from __future__ import annotations

from pathlib import Path

from ..personal_mode import PersonalKernel, PersonalKernelConfig
from ..integration_layer import ControlClient


class LinuxControlClient(ControlClient):
    """Stubbed control client for Linux integration tests."""

    def lookup_agents(self, intent: str, tags):
        return [{"id": "agent-linux", "intent": intent, "tags": tags, "runtime": "sandbox"}]

    def query_resources(self, intent: str, context):
        return {"os": "linux", "cpu_quota": 2, "memory_gb": 4, "context": context}


def bootstrap(policy_path: str | None = None) -> PersonalKernel:
    cfg = PersonalKernelConfig(policy_path=str(Path(policy_path or "policies/linux-personal.json")))
    client = LinuxControlClient()
    return PersonalKernel(config=cfg, control_client=client)


__all__ = ["bootstrap"]
