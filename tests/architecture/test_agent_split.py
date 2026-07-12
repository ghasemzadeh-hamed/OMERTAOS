from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_legacy_agents_root_is_compatibility_only() -> None:
    root = REPO_ROOT / "agents"
    files = sorted(path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file())

    assert files == ["__init__.py"]
    tree = ast.parse((root / "__init__.py").read_text(encoding="utf-8"))
    forbidden = (ast.Import, ast.ImportFrom, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
    assert not any(isinstance(node, forbidden) for node in tree.body)


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
