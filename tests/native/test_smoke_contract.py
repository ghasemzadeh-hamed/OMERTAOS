from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SMOKE = REPO_ROOT / "deploy" / "native" / "scripts" / "smoke-test.sh"


def test_n7_smoke_is_read_only_and_covers_every_native_boundary() -> None:
    text = SMOKE.read_text(encoding="utf-8")
    for marker in (
        "omertaos-install.service",
        "omertaos-runtime.service",
        "omertaos-control.service",
        "omertaos-gateway.service",
        "omertaos-console.service",
        "omertaos.target",
        "postgresql.service",
        "redis-server.service",
        "pg_isready",
        "redis-cli",
        "runtime-daemon --healthcheck",
        "127.0.0.1:8000/healthz",
        "127.0.0.1:8080/health",
        "127.0.0.1:3000/healthz",
        "127.0.0.1:3000/api/system/health",
        "journalctl",
        "NRestarts",
        "journald has no entry",
    ):
        assert marker in text

    for forbidden in (
        "systemctl start",
        "systemctl stop",
        "systemctl restart",
        "systemctl enable",
        "systemctl daemon-reload",
        "prisma migrate deploy",
        "bootstrap-admin.sh",
        "rm -rf",
    ):
        assert forbidden not in text


def test_n7_validates_payloads_not_only_http_status() -> None:
    text = SMOKE.read_text(encoding="utf-8")
    assert "jq -e" in text
    assert '.dependencies.redis == "ok"' in text
    assert '.dependencies.control == "ok"' in text
    assert '.services.console.status == "ok"' in text
    assert '.services.gateway.status == "ok"' in text
    assert '.services.control.status == "ok"' in text


def test_n7_requires_internal_loopback_listeners() -> None:
    text = SMOKE.read_text(encoding="utf-8")
    assert "check_listener 50051 Runtime true" in text
    assert "check_listener 8000 Control true" in text
    assert "check_listener 8080 Gateway false" in text
    assert "check_listener 3000 Console false" in text


def test_capo_smoke_is_a_thin_native_wrapper() -> None:
    wrapper = (REPO_ROOT / "deploy" / "CAPO" / "scripts" / "smoke-test.sh").read_text(encoding="utf-8")
    assert "deploy/native/scripts/smoke-test.sh" in wrapper
    assert len(wrapper.splitlines()) <= 7
