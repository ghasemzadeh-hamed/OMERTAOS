from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from control.app.network.models import Base


def _now() -> datetime:
    return datetime.now(UTC)


class RuntimeNode(Base):
    __tablename__ = "runtime_nodes"

    node_id: Mapped[str] = mapped_column(String(120), primary_key=True)
    endpoint: Mapped[str] = mapped_column(String(255), nullable=False)
    state: Mapped[str] = mapped_column(String(24), nullable=False, default="healthy", index=True)
    software_version: Mapped[str] = mapped_column(String(80), nullable=False, default="unknown")
    contract_version: Mapped[str] = mapped_column(String(80), nullable=False, default="runtime.v1")
    trust_zone: Mapped[str] = mapped_column(String(80), nullable=False, default="local")
    capabilities_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    tenant_ids_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    labels_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    total_cpu_millis: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_memory_mb: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    available_cpu_millis: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    available_memory_mb: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    active_leases: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    drain_requested: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    last_heartbeat_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now, onupdate=_now)

    attempts: Mapped[list["TaskAttempt"]] = relationship(back_populates="node")
    resource_leases: Mapped[list["RuntimeResourceLease"]] = relationship(
        back_populates="node"
    )


class TaskAttempt(Base):
    __tablename__ = "task_attempts"
    __table_args__ = (UniqueConstraint("task_id", "attempt_id", name="uq_task_attempt_identity"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_id: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    attempt_id: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    tenant_id: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    idempotency_key: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    required_capabilities_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    selected_node_id: Mapped[str | None] = mapped_column(ForeignKey("runtime_nodes.node_id"), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="pending", index=True)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now, onupdate=_now)

    node: Mapped[RuntimeNode | None] = relationship(back_populates="attempts")
    resource_lease: Mapped["RuntimeResourceLease | None"] = relationship(
        back_populates="attempt", uselist=False
    )


class RuntimeResourceLease(Base):
    __tablename__ = "runtime_resource_leases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_attempt_id: Mapped[int] = mapped_column(
        ForeignKey("task_attempts.id"), nullable=False, unique=True, index=True
    )
    node_id: Mapped[str] = mapped_column(
        ForeignKey("runtime_nodes.node_id"), nullable=False, index=True
    )
    cpu_millis: Mapped[int] = mapped_column(Integer, nullable=False)
    memory_mb: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(
        String(24), nullable=False, default="active", index=True
    )
    acquired_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now
    )
    released_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    attempt: Mapped[TaskAttempt] = relationship(back_populates="resource_lease")
    node: Mapped[RuntimeNode] = relationship(back_populates="resource_leases")
    execution_lease: Mapped["RuntimeExecutionLease | None"] = relationship(
        back_populates="resource_lease", uselist=False
    )


class RuntimeExecutionLease(Base):
    __tablename__ = "runtime_execution_leases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    resource_lease_id: Mapped[int] = mapped_column(
        ForeignKey("runtime_resource_leases.id"),
        nullable=False,
        unique=True,
        index=True,
    )
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(
        String(24), nullable=False, default="active", index=True
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    resource_lease: Mapped[RuntimeResourceLease] = relationship(
        back_populates="execution_lease"
    )


class SchedulingDecision(Base):
    __tablename__ = "scheduling_decisions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_id: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    attempt_id: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    tenant_id: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    strategy: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    decision: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    selected_node_id: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    eligible_nodes_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    rejected_nodes_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    required_capabilities_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    trace_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)
