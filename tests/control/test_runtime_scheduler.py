from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from control.app.network.migrate import apply_schema, missing_tables
from control.scheduling import (
    NodeState,
    RuntimeNodeHeartbeat,
    RuntimeNodeRegistration,
    RuntimeScheduler,
    SchedulingRequest,
)
from control.scheduling.models import RuntimeNode


@pytest.fixture()
def db() -> Session:
    engine = create_engine("sqlite:///:memory:")
    apply_schema(engine)
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    session = factory()
    try:
        yield session
    finally:
        session.close()


def _register(
    scheduler: RuntimeScheduler,
    db: Session,
    node_id: str,
    *,
    tenants: tuple[str, ...] = (),
    capabilities: tuple[str, ...] = ("terminal.execute",),
    active_leases: int = 0,
    available_cpu: int = 1000,
    available_memory: int = 512,
) -> RuntimeNode:
    node = scheduler.register_node(
        db,
        RuntimeNodeRegistration(
            node_id=node_id,
            endpoint=f"{node_id}:50051",
            tenant_ids=tenants,
            capabilities=capabilities,
            total_cpu_millis=1000,
            total_memory_mb=512,
            available_cpu_millis=available_cpu,
            available_memory_mb=available_memory,
        ),
    )
    node.active_leases = active_leases
    db.commit()
    return node


def test_runtime_scheduler_migration_is_additive_and_idempotent(tmp_path) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'cluster.db'}")

    assert missing_tables(engine) == {
        "control_configuration",
        "proxy_profiles",
        "runtime_nodes",
        "scheduling_decisions",
        "task_attempts",
    }
    apply_schema(engine)
    apply_schema(engine)
    assert missing_tables(engine) == set()


def test_round_robin_scheduler_is_capability_and_tenant_aware(db: Session) -> None:
    scheduler = RuntimeScheduler()
    _register(scheduler, db, "node-a", tenants=("tenant-a",))
    _register(scheduler, db, "node-b", tenants=("tenant-a",))
    _register(scheduler, db, "node-c", tenants=("tenant-b",))

    first = scheduler.schedule(
        db,
        SchedulingRequest(
            task_id="task-1",
            attempt_id="attempt-1",
            tenant_id="tenant-a",
            required_capabilities=("terminal.execute",),
            strategy="round_robin",
        ),
    )
    second = scheduler.schedule(
        db,
        SchedulingRequest(
            task_id="task-2",
            attempt_id="attempt-1",
            tenant_id="tenant-a",
            required_capabilities=("terminal.execute",),
            strategy="round_robin",
        ),
    )

    assert first.selected_node_id == "node-a"
    assert second.selected_node_id == "node-b"
    assert first.rejected_nodes == {"node-c": "tenant"}


def test_least_loaded_scheduler_prefers_capacity_and_health(db: Session) -> None:
    scheduler = RuntimeScheduler()
    _register(
        scheduler, db, "busy", active_leases=3, available_cpu=900, available_memory=500
    )
    _register(
        scheduler,
        db,
        "degraded",
        active_leases=0,
        available_cpu=900,
        available_memory=500,
    )
    _register(
        scheduler, db, "idle", active_leases=0, available_cpu=900, available_memory=500
    )
    scheduler.record_heartbeat(
        db,
        "degraded",
        RuntimeNodeHeartbeat(
            available_cpu_millis=900,
            available_memory_mb=500,
            state=NodeState.degraded,
        ),
    )

    result = scheduler.schedule(
        db,
        SchedulingRequest(
            task_id="task-1",
            attempt_id="attempt-1",
            tenant_id="tenant-a",
            required_capabilities=("terminal.execute",),
            strategy="least_loaded",
        ),
    )

    assert result.selected_node_id == "idle"


def test_scheduler_rejects_draining_stale_and_over_budget_nodes(db: Session) -> None:
    scheduler = RuntimeScheduler(heartbeat_timeout_seconds=5)
    _register(scheduler, db, "draining")
    _register(scheduler, db, "stale")
    _register(scheduler, db, "small", available_cpu=10, available_memory=10)
    scheduler.mark_draining(db, "draining")
    stale = db.get(RuntimeNode, "stale")
    assert stale is not None
    stale.last_heartbeat_at = datetime.now(UTC) - timedelta(seconds=10)
    db.commit()

    result = scheduler.schedule(
        db,
        SchedulingRequest(
            task_id="task-1",
            attempt_id="attempt-1",
            tenant_id="tenant-a",
            required_capabilities=("terminal.execute",),
            cpu_millis=100,
            memory_mb=128,
        ),
    )

    assert result.decision == "rejected"
    assert result.rejected_nodes == {
        "draining": "state:draining",
        "small": "capacity",
        "stale": "state:unreachable",
    }


def test_scheduler_replays_existing_attempt_and_bounds_retry(db: Session) -> None:
    scheduler = RuntimeScheduler()
    _register(scheduler, db, "node-a")
    request = SchedulingRequest(
        task_id="task-1",
        attempt_id="attempt-1",
        tenant_id="tenant-a",
        required_capabilities=("terminal.execute",),
        retry_count=0,
        max_retries=1,
    )

    first = scheduler.schedule(db, request)
    replay = scheduler.schedule(db, request)
    rejected = scheduler.schedule(
        db,
        SchedulingRequest(
            task_id="task-2",
            attempt_id="attempt-1",
            tenant_id="tenant-a",
            retry_count=2,
            max_retries=1,
        ),
    )

    assert first.selected_node_id == "node-a"
    assert replay.selected_node_id == "node-a"
    assert replay.idempotent_replay is True
    assert rejected.decision == "rejected"
    assert rejected.reason == "retry budget exhausted"


def test_scheduler_finishes_attempt_and_releases_node_lease(db: Session) -> None:
    scheduler = RuntimeScheduler()
    _register(scheduler, db, "node-a")
    scheduler.schedule(
        db,
        SchedulingRequest(
            task_id="task-1",
            attempt_id="attempt-1",
            tenant_id="tenant-a",
            required_capabilities=("terminal.execute",),
        ),
    )

    finished = scheduler.finish_attempt(
        db,
        "task-1",
        "attempt-1",
        status="transport_error",
        node_state=NodeState.unreachable,
    )
    replay = scheduler.finish_attempt(
        db,
        "task-1",
        "attempt-1",
        status="transport_error",
        node_state=NodeState.unreachable,
    )
    node = db.get(RuntimeNode, "node-a")

    assert finished.status == "transport_error"
    assert replay.status == "transport_error"
    assert node is not None and node.active_leases == 0
    assert node.state == NodeState.unreachable.value
