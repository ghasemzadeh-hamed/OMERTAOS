from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_quickstart_uses_canonical_runtime_daemon() -> None:
    compose = (REPO_ROOT / "deploy/docker/compose/quickstart.yml").read_text()

    assert "  runtime:\n" in compose
    assert "dockerfile: runtime-daemon/Dockerfile" in compose
    assert "AION_RUNTIME_BIND_ADDR: 0.0.0.0:50051" in compose
    assert "AION_CONTROL_GRPC_BIND: ${AION_CONTROL_GRPC_BIND:-0.0.0.0:50051}" in compose
    assert '"127.0.0.1:50051:50051"' in compose
    assert '["CMD", "/usr/local/bin/runtime-daemon", "--healthcheck"]' in compose
    assert "runtime:\n        condition: service_healthy" in compose
    assert "  kernel:\n" not in compose

    dockerfile = (REPO_ROOT / "runtime-daemon" / "Dockerfile").read_text()
    assert "ENV CARGO_BUILD_JOBS=1" in dockerfile


def test_runtime_daemon_handles_container_stop_gracefully() -> None:
    server = (REPO_ROOT / "runtime-daemon" / "src" / "server.rs").read_text()

    assert ".serve_with_shutdown(addr, shutdown_signal())" in server
    assert "SignalKind::terminate()" in server


def test_quickstart_gateway_declares_development_api_key_map() -> None:
    compose = (REPO_ROOT / "deploy/docker/compose/quickstart.yml").read_text()

    assert "AION_GATEWAY_API_KEYS: ${AION_GATEWAY_API_KEYS:-dev-admin-token:admin}" in compose


def test_gateway_handles_container_stop_gracefully() -> None:
    server = (REPO_ROOT / "gateway" / "src" / "server.ts").read_text()

    assert "process.once('SIGTERM'" in server
    assert "await app.close()" in server
    assert "await closeRedis()" in server
