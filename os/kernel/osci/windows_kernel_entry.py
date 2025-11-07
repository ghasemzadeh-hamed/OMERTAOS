"""Windows kernel entrypoint wiring for CI pipelines."""
from __future__ import annotations

from pathlib import Path

from ..personal_mode import PersonalKernel, PersonalKernelConfig
from ..integration_layer import ControlClient


class StaticControlClient(ControlClient):
    """Stub client for CI that returns static agents and resources."""

    def lookup_agents(self, intent: str, tags):
        return [{"id": "agent-win", "intent": intent, "tags": tags}]

    def query_resources(self, intent: str, context):
        return {"os": "windows", "intent": intent, "context": context}


def bootstrap(personal_policy_path: str | None = None) -> PersonalKernel:
    """Bootstrap a personal kernel for Windows CI."""
    policy_path = Path(personal_policy_path or "policies/windows-personal.json")
    config = PersonalKernelConfig(policy_path=str(policy_path))
    client = StaticControlClient()
    return PersonalKernel(config=config, control_client=client)


__all__ = ["bootstrap"]
