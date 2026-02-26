from __future__ import annotations

from pathlib import Path

import pytest

from control.config_paths import resolve_config_path
from kernel.governance_hook import GovernanceHook
from kernel.integration_layer import ControlClient, IntegrationLayer
from kernel.policy_engine import PolicyEngine
from kernel.router.ai_router import AIRouter


class _TestControlClient(ControlClient):
    def lookup_agents(self, intent: str, tags):
        return [{"id": "test-agent", "intent": intent, "tags": tags}]

    def query_resources(self, intent: str, context):
        return {"intent": intent, "context": context}


def test_resolve_config_path_prefers_repo(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AION_CONFIG_PATH", raising=False)
    path = resolve_config_path()
    expected = Path.cwd() / "config" / "aion.config.yaml"
    assert path == expected
    assert path.exists()


def test_resolve_config_path_honours_env_for_writes(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    target = tmp_path / "custom" / "aion.config.yaml"
    monkeypatch.setenv("AION_CONFIG_PATH", str(target))
    resolved = resolve_config_path(prefer_existing=False)
    assert resolved == target


def test_airouter_constructs_with_kernel_dependencies() -> None:
    router = AIRouter(
        policy_engine=PolicyEngine(policy_path=Path("policies/linux-personal.json")),
        governance_hook=GovernanceHook(),
        integration_layer=IntegrationLayer(control_client=_TestControlClient()),
    )
    assert router.health() == {"status": "ok", "component": "ai_router"}
