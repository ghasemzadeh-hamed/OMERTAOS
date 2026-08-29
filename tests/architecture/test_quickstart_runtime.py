from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_quickstart_uses_canonical_runtime_daemon() -> None:
    compose = (REPO_ROOT / "deploy/docker/compose/quickstart.yml").read_text()

    assert "  runtime:\n" in compose
    assert "dockerfile: runtime-daemon/Dockerfile" in compose
    assert "AION_RUNTIME_BIND_ADDR: 0.0.0.0:50051" in compose
    assert "AION_CONTROL_GRPC_BIND: ${AION_CONTROL_GRPC_BIND:-0.0.0.0:50051}" in compose
    assert '"127.0.0.1:${AION_RUNTIME_HOST_PORT:-50051}:50051"' in compose
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


def test_quickstart_applies_console_migrations_before_control() -> None:
    compose = (REPO_ROOT / "deploy/docker/compose/quickstart.yml").read_text()
    control = compose.split("  control:\n", maxsplit=1)[1].split(
        "  gateway:\n", maxsplit=1
    )[0]

    assert "      install:\n        condition: service_completed_successfully" in control


def test_gateway_image_uses_locked_audited_dependency_install() -> None:
    dockerfile_bytes = (REPO_ROOT / "gateway" / "Dockerfile").read_bytes()

    assert not dockerfile_bytes.startswith(b"\xef\xbb\xbf")

    dockerfile = dockerfile_bytes.decode("utf-8")
    assert (
        "RUN --mount=type=cache,target=/root/.npm,sharing=locked npm ci"
        in dockerfile
    )
    assert "npm install" not in dockerfile
    assert "--no-audit" not in dockerfile


def test_quickstart_supports_an_isolated_local_stack() -> None:
    compose = (REPO_ROOT / "deploy/docker/compose/quickstart.yml").read_text()

    assert '"${AION_CONTROL_HOST_PORT:-8000}:8000"' in compose
    assert '"${AION_GATEWAY_HOST_PORT:-8080}:8080"' in compose
    assert '"${AION_CONSOLE_HOST_PORT:-3000}:3000"' in compose
    assert "image: ${AION_CONSOLE_IMAGE:-omertaos-console}" in compose
    assert "AION_CORS_ORIGINS: ${AION_CORS_ORIGINS:-http://localhost:3000}" in compose
    assert "NEXTAUTH_URL: ${NEXTAUTH_URL:-http://localhost:3000}" in compose
    assert (
        "NEXT_PUBLIC_GATEWAY_URL: "
        "${NEXT_PUBLIC_GATEWAY_URL:-http://localhost:8080}" in compose
    )
    assert "name: ${AION_DOCKER_NETWORK:-omerta-net}" in compose


def test_gateway_handles_container_stop_gracefully() -> None:
    server = (REPO_ROOT / "gateway" / "src" / "server.ts").read_text()

    assert "process.once('SIGTERM'" in server
    assert "await app.close()" in server
    assert "await closeRedis()" in server
