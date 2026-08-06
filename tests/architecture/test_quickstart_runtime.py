from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_quickstart_uses_canonical_runtime_daemon() -> None:
    compose = (REPO_ROOT / "deploy/docker/compose/quickstart.yml").read_text()

    assert "  runtime:\n" in compose
    assert "dockerfile: runtime-daemon/Dockerfile" in compose
    assert "AION_RUNTIME_BIND_ADDR: 0.0.0.0:50051" in compose
    assert '"127.0.0.1:50051:50051"' in compose
    assert '["CMD", "/usr/local/bin/runtime-daemon", "--healthcheck"]' in compose
    assert "runtime:\n        condition: service_healthy" in compose
    assert "  kernel:\n" not in compose
