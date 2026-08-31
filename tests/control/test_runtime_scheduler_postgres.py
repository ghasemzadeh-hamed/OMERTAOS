from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker

from control.app.network.migrate import apply_schema
from control.scheduling import (
    RuntimeNodeRegistration,
    RuntimeScheduler,
    SchedulingRequest,
)
from control.scheduling.models import RuntimeNode, RuntimeResourceLease


POSTGRES_DSN = os.getenv("AION_TEST_POSTGRES_DSN")
pytestmark = pytest.mark.skipif(
    not POSTGRES_DSN,
    reason="AION_TEST_POSTGRES_DSN is required for scheduler concurrency tests",
)


def _schedule_concurrently(
    factory: sessionmaker[Session], requests: list[SchedulingRequest]
) -> list[object]:
    ready = Barrier(len(requests))

    def schedule(request: SchedulingRequest) -> object:
        ready.wait(timeout=10)
        with factory() as db:
            return RuntimeScheduler(heartbeat_timeout_seconds=120).schedule(
                db, request, actor="scheduler-concurrency-test"
            )

    with ThreadPoolExecutor(max_workers=len(requests)) as pool:
        return list(pool.map(schedule, requests))


def test_postgres_scheduler_serializes_identity_and_capacity() -> None:
    assert POSTGRES_DSN is not None
    engine = create_engine(POSTGRES_DSN, future=True)
    apply_schema(engine)
    factory = sessionmaker(
        bind=engine, autoflush=False, autocommit=False, future=True
    )
    scheduler = RuntimeScheduler(heartbeat_timeout_seconds=120)
    run_id = uuid4().hex
    node_id = f"scheduler-concurrency-{run_id}"
    tenant_id = f"scheduler-concurrency-{run_id}"
    capability = f"scheduler.concurrent.{run_id}"

    with factory() as db:
        scheduler.register_node(
            db,
            RuntimeNodeRegistration(
                node_id=node_id,
                endpoint="scheduler-concurrency.invalid:50051",
                tenant_ids=(tenant_id,),
                capabilities=(capability,),
                total_cpu_millis=1000,
                total_memory_mb=512,
            ),
            actor="scheduler-concurrency-test",
        )

    shared_request = SchedulingRequest(
        task_id=f"shared-{run_id}",
        attempt_id="attempt-1",
        tenant_id=tenant_id,
        required_capabilities=(capability,),
        cpu_millis=600,
        memory_mb=300,
    )
    shared_results = _schedule_concurrently(
        factory, [shared_request, shared_request]
    )

    assert [result.decision for result in shared_results] == ["selected", "selected"]
    assert sorted(result.idempotent_replay for result in shared_results) == [
        False,
        True,
    ]
    with factory() as db:
        node = db.get(RuntimeNode, node_id)
        assert node is not None and node.active_leases == 1
        assert node.available_cpu_millis == 400
        assert node.available_memory_mb == 212
        scheduler.finish_attempt(
            db,
            shared_request.task_id,
            shared_request.attempt_id,
            tenant_id=tenant_id,
            status="completed",
            actor="scheduler-concurrency-test",
        )

    capacity_requests = [
        SchedulingRequest(
            task_id=f"capacity-{run_id}-{index}",
            attempt_id="attempt-1",
            tenant_id=tenant_id,
            required_capabilities=(capability,),
            cpu_millis=600,
            memory_mb=300,
        )
        for index in range(2)
    ]
    capacity_results = _schedule_concurrently(factory, capacity_requests)

    assert sorted(result.decision for result in capacity_results) == [
        "rejected",
        "selected",
    ]
    selected_request = next(
        request
        for request, result in zip(capacity_requests, capacity_results, strict=True)
        if result.decision == "selected"
    )
    with factory() as db:
        node = db.get(RuntimeNode, node_id)
        assert node is not None and node.active_leases == 1
        assert node.available_cpu_millis == 400
        assert node.available_memory_mb == 212
        scheduler.finish_attempt(
            db,
            selected_request.task_id,
            selected_request.attempt_id,
            tenant_id=tenant_id,
            status="completed",
            actor="scheduler-concurrency-test",
        )
        db.expire_all()
        node = db.get(RuntimeNode, node_id)
        active_leases = db.scalar(
            select(func.count(RuntimeResourceLease.id))
            .where(RuntimeResourceLease.node_id == node_id)
            .where(RuntimeResourceLease.status == "active")
        )
        assert node is not None and node.active_leases == 0
        assert node.available_cpu_millis == 1000
        assert node.available_memory_mb == 512
        assert active_leases == 0

    engine.dispose()
