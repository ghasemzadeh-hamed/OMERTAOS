from __future__ import annotations

import ast
from datetime import UTC
from pathlib import Path

from integrations.observability.exporter import TelemetryExporter
from shared.telemetry.audit import AuditEntry, emit_audit
from shared.telemetry.bus import TelemetryBus

REPO_ROOT = Path(__file__).resolve().parents[2]


def _top_level_implementations(root: Path) -> list[str]:
    violations: list[str] = []
    for path in root.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in tree.body:
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                violations.append(f"{path.relative_to(REPO_ROOT).as_posix()}: {node.name}")
    return violations


def test_legacy_observability_roots_are_compatibility_only() -> None:
    violations = _top_level_implementations(REPO_ROOT / "observability")
    violations.extend(_top_level_implementations(REPO_ROOT / "shared" / "event_bus"))

    assert not violations, "legacy observability implementation remains: " + ", ".join(violations)


def test_legacy_observability_roots_are_retired() -> None:
    assert not (REPO_ROOT / "observability").exists()
    assert not (REPO_ROOT / "shared" / "event_bus").exists()


def test_audit_primitive_preserves_actor_and_tenant_scope() -> None:
    entry = emit_audit("network.proxy_profile.create", "admin-a", "tenant-a")

    assert entry == AuditEntry(
        action="network.proxy_profile.create",
        actor="admin-a",
        tenant_id="tenant-a",
        at=entry.at,
    )
    assert entry.at.tzinfo is UTC


def test_telemetry_bus_dispatches_without_mutating_payload() -> None:
    bus = TelemetryBus()
    received: list[dict[str, object]] = []
    payload: dict[str, object] = {"tenant_id": "tenant-a", "metric": 1}

    bus.subscribe("metric.recorded", received.append)
    bus.publish("metric.recorded", payload)

    assert received == [payload]
    assert received[0] is payload


def test_control_and_deployment_use_canonical_observability_owners() -> None:
    service = (REPO_ROOT / "control" / "app" / "network" / "service.py").read_text(encoding="utf-8")
    dockerfile = (REPO_ROOT / "control" / "Dockerfile").read_text(encoding="utf-8")
    legacy_imports: list[str] = []

    for path in (REPO_ROOT / "control").rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("observability"):
                legacy_imports.append(path.relative_to(REPO_ROOT).as_posix())
            elif isinstance(node, ast.Import):
                legacy_imports.extend(
                    path.relative_to(REPO_ROOT).as_posix()
                    for alias in node.names
                    if alias.name.startswith("observability")
                )

    assert "from shared.telemetry.audit import emit_audit" in service
    assert not legacy_imports, "Control imports legacy observability root: " + ", ".join(legacy_imports)
    assert "COPY shared ./shared" in dockerfile
    assert "COPY observability ./observability" not in dockerfile

    deploy_root = REPO_ROOT / "deploy" / "observability"
    assert (deploy_root / "otel-collector.yaml").is_file()
    assert (deploy_root / "prometheus.yml").is_file()
    assert (deploy_root / "grafana" / "router.json").is_file()
