from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import DateTime, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from control.app.network.models import Base


def _now() -> datetime:
    return datetime.now(UTC)


class RuntimeAuditEvent(Base):
    __tablename__ = "runtime_audit_events"
    __table_args__ = (
        Index(
            "ix_runtime_audit_task_tenant_created",
            "task_id",
            "tenant_id",
            "created_at",
            "id",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_id: Mapped[str] = mapped_column(
        String(36), nullable=False, unique=True, index=True, default=lambda: str(uuid4())
    )
    action: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    actor: Mapped[str] = mapped_column(String(120), nullable=False)
    tenant_id: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    task_id: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    attempt_id: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    node_id: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    request_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    trace_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    outcome: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now, index=True
    )
