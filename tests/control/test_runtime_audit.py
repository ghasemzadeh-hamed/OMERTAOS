from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from control.app.network.migrate import apply_schema
from control.audit.models import RuntimeAuditEvent
from control.audit.service import (
    MAX_AUDIT_EVENTS_PER_TASK,
    append_runtime_audit_event,
    list_runtime_audit_events,
)


def test_runtime_audit_schema_excludes_payload_and_secret_fields() -> None:
    columns = set(RuntimeAuditEvent.__table__.columns.keys())

    assert {
        "event_id",
        "action",
        "actor",
        "tenant_id",
        "task_id",
        "attempt_id",
        "node_id",
        "request_id",
        "trace_id",
        "outcome",
        "reason",
        "retry_count",
        "created_at",
    }.issubset(columns)
    assert columns.isdisjoint(
        {
            "message",
            "payload",
            "stdout",
            "stderr",
            "idempotency_key",
            "credential",
            "secret",
            "token",
        }
    )


def test_runtime_audit_listing_is_ordered_tenant_scoped_and_bounded() -> None:
    engine = create_engine("sqlite:///:memory:")
    apply_schema(engine)

    with Session(engine) as db:
        for index in range(MAX_AUDIT_EVENTS_PER_TASK + 2):
            append_runtime_audit_event(
                db,
                action="runtime.schedule",
                actor="agent-a",
                tenant_id="tenant-a",
                task_id="task-a",
                attempt_id=f"attempt-{index}",
                outcome="selected",
                reason="eligible runtime node selected",
                retry_count=index,
            )
        append_runtime_audit_event(
            db,
            action="runtime.schedule",
            actor="agent-b",
            tenant_id="tenant-b",
            task_id="task-a",
            outcome="rejected",
            reason="no eligible runtime node",
        )
        db.commit()

        events = list_runtime_audit_events(
            db,
            task_id="task-a",
            tenant_id="tenant-a",
        )
        assert len(events) == MAX_AUDIT_EVENTS_PER_TASK
        assert [event.retry_count for event in events] == list(
            range(MAX_AUDIT_EVENTS_PER_TASK)
        )
        assert list_runtime_audit_events(
            db,
            task_id="task-a",
            tenant_id="tenant-c",
        ) == []
