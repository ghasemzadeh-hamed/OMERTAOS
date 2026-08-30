from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import RuntimeAuditEvent

MAX_AUDIT_EVENTS_PER_TASK = 100


def append_runtime_audit_event(
    db: Session,
    *,
    action: str,
    actor: str,
    tenant_id: str,
    task_id: str,
    outcome: str,
    reason: str,
    attempt_id: str | None = None,
    node_id: str | None = None,
    request_id: str | None = None,
    trace_id: str | None = None,
    retry_count: int = 0,
) -> RuntimeAuditEvent:
    event = RuntimeAuditEvent(
        action=action,
        actor=actor,
        tenant_id=tenant_id,
        task_id=task_id,
        attempt_id=attempt_id,
        node_id=node_id,
        request_id=request_id or None,
        trace_id=trace_id or None,
        outcome=outcome,
        reason=reason,
        retry_count=retry_count,
    )
    db.add(event)
    return event


def list_runtime_audit_events(
    db: Session,
    *,
    task_id: str,
    tenant_id: str,
) -> list[RuntimeAuditEvent]:
    return list(
        db.scalars(
            select(RuntimeAuditEvent)
            .where(RuntimeAuditEvent.task_id == task_id)
            .where(RuntimeAuditEvent.tenant_id == tenant_id)
            .order_by(RuntimeAuditEvent.created_at, RuntimeAuditEvent.id)
            .limit(MAX_AUDIT_EVENTS_PER_TASK)
        ).all()
    )
