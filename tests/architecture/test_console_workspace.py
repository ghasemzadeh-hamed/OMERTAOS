from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_console_pnpm_workspace_declares_package_roots() -> None:
    workspace = yaml.safe_load((REPO_ROOT / "console" / "pnpm-workspace.yaml").read_text())

    assert workspace["packages"] == ["."]
