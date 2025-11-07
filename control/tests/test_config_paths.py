from __future__ import annotations

from pathlib import Path

import pytest

from os.control.config_paths import resolve_config_path
from os.control.ai_router import AIRouter


def test_resolve_config_path_prefers_repo(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AIONOS_CONFIG_PATH", raising=False)
    path = resolve_config_path()
    expected = Path.cwd() / "config" / "aionos.config.yaml"
    assert path == expected
    assert path.exists()


def test_resolve_config_path_honours_env_for_writes(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    target = tmp_path / "custom" / "aionos.config.yaml"
    monkeypatch.setenv("AIONOS_CONFIG_PATH", str(target))
    resolved = resolve_config_path(prefer_existing=False)
    assert resolved == target


def test_airouter_uses_fallback_config(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AIONOS_CONFIG_PATH", raising=False)
    router = AIRouter()
    assert router.local.model == "llama3.2:3b"
