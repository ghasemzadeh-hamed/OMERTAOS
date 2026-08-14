from __future__ import annotations

import ast
import asyncio
import json
from pathlib import Path

import pytest

from control.ports.event_bus import DomainEvent
from integrations.eventbus.kafka import KafkaEventBus
from integrations.eventbus.local import LocalEventBus

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_legacy_eventbus_root_is_compatibility_only() -> None:
    violations: list[str] = []
    for path in (REPO_ROOT / "eventbus").glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in tree.body:
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                violations.append(f"{path.name}: {node.name}")

    assert not violations, "legacy EventBus implementation remains: " + ", ".join(violations)


def test_legacy_eventbus_root_is_retired() -> None:
    assert not (REPO_ROOT / "eventbus").exists()


@pytest.mark.asyncio
async def test_local_adapter_dispatches_tenant_scoped_event() -> None:
    bus = LocalEventBus()
    received: list[DomainEvent] = []
    dispatched = asyncio.Event()

    async def handle(event: DomainEvent) -> None:
        received.append(event)
        dispatched.set()

    await bus.subscribe("task.created", handle)
    event = DomainEvent("task.created", "tenant-a", {"task_id": "task-1"})
    await bus.publish(event)
    await asyncio.wait_for(dispatched.wait(), timeout=1)

    assert received == [event]
    assert received[0].tenant_id == "tenant-a"
    assert received[0].occurred_at.endswith("+00:00")


@pytest.mark.asyncio
async def test_unwired_kafka_adapter_fails_closed() -> None:
    bus = KafkaEventBus("kafka:9092")
    event = DomainEvent("task.created", "tenant-a", {})

    async def handle(_event: DomainEvent) -> None:
        return None

    with pytest.raises(NotImplementedError, match="aiokafka producer"):
        await bus.publish(event)
    with pytest.raises(NotImplementedError, match="aiokafka consumer"):
        await bus.subscribe("task.created", handle)


def test_canonical_eventbus_modules_do_not_import_legacy_root() -> None:
    roots = (REPO_ROOT / "control" / "ports", REPO_ROOT / "integrations" / "eventbus")
    violations: list[str] = []

    for root in roots:
        for path in root.glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("eventbus"):
                    violations.append(path.relative_to(REPO_ROOT).as_posix())
                elif isinstance(node, ast.Import):
                    violations.extend(
                        path.relative_to(REPO_ROOT).as_posix()
                        for alias in node.names
                        if alias.name.startswith("eventbus")
                    )

    assert not violations, "canonical EventBus code imports legacy root: " + ", ".join(violations)


def test_event_contract_sources_remain_versioned_and_parseable() -> None:
    root = REPO_ROOT / "schemas" / "v1" / "events"
    expected = {
        "audit_activity.schema.json",
        "metrics_runtime.schema.json",
        "router_decision.schema.json",
        "tasks_lifecycle.schema.json",
    }
    paths = {path.name for path in root.glob("*.schema.json")}

    assert paths == expected
    for name in expected:
        schema = json.loads((root / name).read_text(encoding="utf-8"))
        assert schema["$schema"] == "http://json-schema.org/draft-07/schema#"
        assert schema["type"] == "object"
        assert schema["required"]
