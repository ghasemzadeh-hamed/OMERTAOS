from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_legacy_agents_root_is_retired() -> None:
    assert not (REPO_ROOT / "agents").exists()


def test_agent_ownership_contract_lists_every_behavior_class() -> None:
    contract = (REPO_ROOT / "docs" / "migration" / "agents-split.md").read_text(encoding="utf-8")
    for owner in (
        "registry/agents/",
        "control/agents/",
        "packages/agent-sdk/",
        "integrations/agents/",
        "runtime-daemon/",
    ):
        assert owner in contract
