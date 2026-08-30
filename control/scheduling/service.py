from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from control.audit import append_runtime_audit_event
from shared.telemetry.audit import emit_audit

from .models import RuntimeNode, SchedulingDecision, TaskAttempt


class NodeState(str, Enum):
    healthy = "healthy"
    degraded = "degraded"
    unreachable = "unreachable"
    draining = "draining"


@dataclass(frozen=True, slots=True)
class RuntimeNodeRegistration:
    node_id: str
    endpoint: str
    capabilities: tuple[str, ...] = ()
    total_cpu_millis: int = 1000
    total_memory_mb: int = 512
    available_cpu_millis: int | None = None
    available_memory_mb: int | None = None
    tenant_ids: tuple[str, ...] = ()
    software_version: str = "unknown"
    contract_version: str = "runtime.v1"
    trust_zone: str = "local"
    labels: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _require_text(self.node_id, "node_id")
        _require_text(self.endpoint, "endpoint")
        _require_positive(self.total_cpu_millis, "total_cpu_millis")
        _require_positive(self.total_memory_mb, "total_memory_mb")
        if self.available_cpu_millis is not None and self.available_cpu_millis < 0:
            raise ValueError("available_cpu_millis must be non-negative")
        if self.available_memory_mb is not None and self.available_memory_mb < 0:
            raise ValueError("available_memory_mb must be non-negative")


@dataclass(frozen=True, slots=True)
class RuntimeNodeHeartbeat:
    available_cpu_millis: int
    available_memory_mb: int
    active_leases: int = 0
    state: NodeState = NodeState.healthy
    capabilities: tuple[str, ...] | None = None

    def __post_init__(self) -> None:
        if self.available_cpu_millis < 0:
            raise ValueError("available_cpu_millis must be non-negative")
        if self.available_memory_mb < 0:
            raise ValueError("available_memory_mb must be non-negative")
        if self.active_leases < 0:
            raise ValueError("active_leases must be non-negative")


@dataclass(frozen=True, slots=True)
class SchedulingRequest:
    task_id: str
    attempt_id: str
    tenant_id: str
    required_capabilities: tuple[str, ...] = ()
    cpu_millis: int = 100
    memory_mb: int = 128
    strategy: str = "round_robin"
    idempotency_key: str | None = None
    retry_count: int = 0
    max_retries: int = 0
    trace_id: str | None = None

    def __post_init__(self) -> None:
        _require_text(self.task_id, "task_id")
        _require_text(self.attempt_id, "attempt_id")
        _require_text(self.tenant_id, "tenant_id")
        _require_positive(self.cpu_millis, "cpu_millis")
        _require_positive(self.memory_mb, "memory_mb")
        if self.strategy not in {"round_robin", "least_loaded"}:
            raise ValueError("strategy must be round_robin or least_loaded")
        if self.retry_count < 0 or self.max_retries < 0:
            raise ValueError("retry counts must be non-negative")


@dataclass(frozen=True, slots=True)
class SchedulingResult:
    task_id: str
    attempt_id: str
    tenant_id: str
    strategy: str
    decision: str
    selected_node_id: str | None
    reason: str
    eligible_nodes: tuple[str, ...]
    rejected_nodes: dict[str, str]
    idempotent_replay: bool = False


def _require_text(value: str, field_name: str) -> None:
    if not value.strip():
        raise ValueError(f"{field_name} is required")


def _require_positive(value: int, field_name: str) -> None:
    if value <= 0:
        raise ValueError(f"{field_name} must be positive")


def _now() -> datetime:
    return datetime.now(UTC)


def _json_list(values: tuple[str, ...] | list[str]) -> str:
    normalized = sorted({value.strip() for value in values if value.strip()})
    return json.dumps(normalized, separators=(",", ":"))


def _json_map(values: dict[str, str]) -> str:
    normalized = {key: values[key] for key in sorted(values)}
    return json.dumps(normalized, separators=(",", ":"))


def _list(raw: str) -> set[str]:
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return set()
    if not isinstance(parsed, list):
        return set()
    return {str(item) for item in parsed if str(item).strip()}


def _state(node: RuntimeNode) -> NodeState:
    try:
        return NodeState(node.state)
    except ValueError:
        return NodeState.unreachable


class RuntimeScheduler:
    def __init__(self, *, heartbeat_timeout_seconds: int = 30) -> None:
        if heartbeat_timeout_seconds <= 0:
            raise ValueError("heartbeat_timeout_seconds must be positive")
        self.heartbeat_timeout = timedelta(seconds=heartbeat_timeout_seconds)

    def register_node(
        self,
        db: Session,
        registration: RuntimeNodeRegistration,
        *,
        actor: str = "system",
    ) -> RuntimeNode:
        available_cpu = registration.available_cpu_millis
        available_memory = registration.available_memory_mb
        node = db.get(RuntimeNode, registration.node_id)
        if node is None:
            node = RuntimeNode(node_id=registration.node_id, endpoint=registration.endpoint)
            db.add(node)
        node.endpoint = registration.endpoint
        node.state = NodeState.healthy.value
        node.software_version = registration.software_version
        node.contract_version = registration.contract_version
        node.trust_zone = registration.trust_zone
        node.capabilities_json = _json_list(registration.capabilities)
        node.tenant_ids_json = _json_list(registration.tenant_ids)
        node.labels_json = _json_map(registration.labels)
        node.total_cpu_millis = registration.total_cpu_millis
        node.total_memory_mb = registration.total_memory_mb
        node.available_cpu_millis = available_cpu if available_cpu is not None else registration.total_cpu_millis
        node.available_memory_mb = available_memory if available_memory is not None else registration.total_memory_mb
        node.drain_requested = False
        node.last_heartbeat_at = _now()
        node.updated_at = _now()
        db.commit()
        db.refresh(node)
        emit_audit("runtime.node.register", actor, "system")
        return node

    def record_heartbeat(
        self,
        db: Session,
        node_id: str,
        heartbeat: RuntimeNodeHeartbeat,
        *,
        actor: str = "system",
    ) -> RuntimeNode:
        node = db.get(RuntimeNode, node_id)
        if node is None:
            raise ValueError("runtime node is not registered")
        if node.drain_requested or heartbeat.state is NodeState.draining:
            node.state = NodeState.draining.value
            node.drain_requested = True
        else:
            node.state = heartbeat.state.value
        node.available_cpu_millis = heartbeat.available_cpu_millis
        node.available_memory_mb = heartbeat.available_memory_mb
        node.active_leases = heartbeat.active_leases
        if heartbeat.capabilities is not None:
            node.capabilities_json = _json_list(heartbeat.capabilities)
        node.last_heartbeat_at = _now()
        node.updated_at = _now()
        db.commit()
        db.refresh(node)
        emit_audit("runtime.node.heartbeat", actor, "system")
        return node

    def mark_draining(self, db: Session, node_id: str, *, actor: str = "system") -> RuntimeNode:
        node = db.get(RuntimeNode, node_id)
        if node is None:
            raise ValueError("runtime node is not registered")
        node.state = NodeState.draining.value
        node.drain_requested = True
        node.updated_at = _now()
        db.commit()
        db.refresh(node)
        emit_audit("runtime.node.drain", actor, "system")
        return node

    def refresh_unreachable(self, db: Session, *, at: datetime | None = None) -> int:
        checked_at = at or _now()
        changed = 0
        for node in db.scalars(select(RuntimeNode)).all():
            if _state(node) is NodeState.draining:
                continue
            if node.last_heartbeat_at is None or checked_at - _as_aware(node.last_heartbeat_at) > self.heartbeat_timeout:
                if node.state != NodeState.unreachable.value:
                    node.state = NodeState.unreachable.value
                    node.updated_at = checked_at
                    changed += 1
        if changed:
            db.commit()
        return changed

    def discover_workers(self, db: Session, tenant_id: str) -> list[RuntimeNode]:
        self.refresh_unreachable(db)
        nodes = db.scalars(select(RuntimeNode).order_by(RuntimeNode.node_id)).all()
        return [node for node in nodes if self._tenant_allowed(node, tenant_id)]

    def get_attempt(
        self,
        db: Session,
        task_id: str,
        attempt_id: str,
    ) -> TaskAttempt | None:
        return db.scalars(
            select(TaskAttempt)
            .where(TaskAttempt.task_id == task_id)
            .where(TaskAttempt.attempt_id == attempt_id)
        ).first()

    def finish_attempt(
        self,
        db: Session,
        task_id: str,
        attempt_id: str,
        *,
        status: str,
        node_state: NodeState | None = None,
        actor: str = "system",
        audit_action: str = "runtime.attempt.finish",
        request_id: str | None = None,
        trace_id: str | None = None,
        reason: str = "runtime attempt finished",
    ) -> TaskAttempt:
        _require_text(status, "status")
        attempt = self.get_attempt(db, task_id, attempt_id)
        if attempt is None:
            raise ValueError("runtime attempt is not registered")
        node = attempt.node
        if attempt.status == "leased" and node is not None:
            node.active_leases = max(node.active_leases - 1, 0)
        attempt.status = status
        attempt.updated_at = _now()
        if (
            node is not None
            and node_state is not None
            and _state(node) is not NodeState.draining
        ):
            node.state = node_state.value
            node.updated_at = _now()
        append_runtime_audit_event(
            db,
            action=audit_action,
            actor=actor,
            tenant_id=attempt.tenant_id,
            task_id=attempt.task_id,
            attempt_id=attempt.attempt_id,
            node_id=attempt.selected_node_id,
            request_id=request_id,
            trace_id=trace_id,
            outcome=status,
            reason=reason,
            retry_count=attempt.retry_count,
        )
        db.commit()
        db.refresh(attempt)
        emit_audit("runtime.attempt.finish", actor, attempt.tenant_id)
        return attempt

    def schedule(self, db: Session, request: SchedulingRequest, *, actor: str = "system") -> SchedulingResult:
        existing = self.get_attempt(db, request.task_id, request.attempt_id)
        if existing and existing.selected_node_id:
            return self._record_decision(
                db,
                request,
                "selected",
                existing.selected_node_id,
                "idempotent scheduling replay",
                (existing.selected_node_id,),
                {},
                actor,
                idempotent_replay=True,
            )

        if request.retry_count > request.max_retries:
            return self._record_decision(
                db,
                request,
                "rejected",
                None,
                "retry budget exhausted",
                (),
                {},
                actor,
            )

        attempt = existing or TaskAttempt(
            task_id=request.task_id,
            attempt_id=request.attempt_id,
            tenant_id=request.tenant_id,
        )
        attempt.idempotency_key = request.idempotency_key
        attempt.required_capabilities_json = _json_list(request.required_capabilities)
        attempt.retry_count = request.retry_count
        attempt.max_retries = request.max_retries
        if existing is None:
            db.add(attempt)

        eligible, rejected = self._eligible_nodes(db, request)
        if not eligible:
            attempt.status = "pending"
            db.flush()
            return self._record_decision(
                db,
                request,
                "rejected",
                None,
                "no eligible runtime node",
                (),
                rejected,
                actor,
            )

        selected = self._select_node(db, request.strategy, eligible, request.tenant_id)
        selected.active_leases += 1
        attempt.selected_node_id = selected.node_id
        attempt.status = "leased"
        attempt.updated_at = _now()
        db.flush()
        return self._record_decision(
            db,
            request,
            "selected",
            selected.node_id,
            "eligible runtime node selected",
            tuple(node.node_id for node in eligible),
            rejected,
            actor,
        )

    def _eligible_nodes(self, db: Session, request: SchedulingRequest) -> tuple[list[RuntimeNode], dict[str, str]]:
        self.refresh_unreachable(db)
        required = set(request.required_capabilities)
        eligible: list[RuntimeNode] = []
        rejected: dict[str, str] = {}
        for node in db.scalars(select(RuntimeNode).order_by(RuntimeNode.node_id)).all():
            state = _state(node)
            if state in {NodeState.unreachable, NodeState.draining}:
                rejected[node.node_id] = f"state:{state.value}"
                continue
            if not self._tenant_allowed(node, request.tenant_id):
                rejected[node.node_id] = "tenant"
                continue
            node_capabilities = _list(node.capabilities_json)
            if not required.issubset(node_capabilities):
                rejected[node.node_id] = "capability"
                continue
            if node.available_cpu_millis < request.cpu_millis or node.available_memory_mb < request.memory_mb:
                rejected[node.node_id] = "capacity"
                continue
            eligible.append(node)
        return eligible, rejected

    def _select_node(
        self,
        db: Session,
        strategy: str,
        eligible: list[RuntimeNode],
        tenant_id: str,
    ) -> RuntimeNode:
        if strategy == "least_loaded":
            return min(
                eligible,
                key=lambda node: (
                    _state(node) is NodeState.degraded,
                    node.active_leases,
                    _utilization(node),
                    node.node_id,
                ),
            )

        ordered = sorted(eligible, key=lambda node: (_state(node) is NodeState.degraded, node.node_id))
        previous = db.scalars(
            select(SchedulingDecision)
            .where(SchedulingDecision.tenant_id == tenant_id)
            .where(SchedulingDecision.strategy == "round_robin")
            .where(SchedulingDecision.selected_node_id.is_not(None))
            .order_by(desc(SchedulingDecision.created_at), desc(SchedulingDecision.id))
        ).first()
        if not previous or previous.selected_node_id not in {node.node_id for node in ordered}:
            return ordered[0]
        previous_index = [node.node_id for node in ordered].index(previous.selected_node_id)
        return ordered[(previous_index + 1) % len(ordered)]

    def _tenant_allowed(self, node: RuntimeNode, tenant_id: str) -> bool:
        tenants = _list(node.tenant_ids_json)
        return not tenants or tenant_id in tenants

    def _record_decision(
        self,
        db: Session,
        request: SchedulingRequest,
        decision: str,
        selected_node_id: str | None,
        reason: str,
        eligible_nodes: tuple[str, ...],
        rejected_nodes: dict[str, str],
        actor: str,
        *,
        idempotent_replay: bool = False,
    ) -> SchedulingResult:
        row = SchedulingDecision(
            task_id=request.task_id,
            attempt_id=request.attempt_id,
            tenant_id=request.tenant_id,
            strategy=request.strategy,
            decision=decision,
            selected_node_id=selected_node_id,
            reason=reason,
            eligible_nodes_json=_json_list(eligible_nodes),
            rejected_nodes_json=_json_map(rejected_nodes),
            required_capabilities_json=_json_list(request.required_capabilities),
            trace_id=request.trace_id,
        )
        db.add(row)
        append_runtime_audit_event(
            db,
            action="runtime.schedule",
            actor=actor,
            tenant_id=request.tenant_id,
            task_id=request.task_id,
            attempt_id=request.attempt_id,
            node_id=selected_node_id,
            trace_id=request.trace_id,
            outcome=decision,
            reason=reason,
            retry_count=request.retry_count,
        )
        db.commit()
        emit_audit("runtime.schedule", actor, request.tenant_id)
        return SchedulingResult(
            task_id=request.task_id,
            attempt_id=request.attempt_id,
            tenant_id=request.tenant_id,
            strategy=request.strategy,
            decision=decision,
            selected_node_id=selected_node_id,
            reason=reason,
            eligible_nodes=eligible_nodes,
            rejected_nodes=rejected_nodes,
            idempotent_replay=idempotent_replay,
        )


def _as_aware(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value


def _utilization(node: RuntimeNode) -> float:
    cpu_total = max(node.total_cpu_millis, 1)
    mem_total = max(node.total_memory_mb, 1)
    cpu_used = max(node.total_cpu_millis - node.available_cpu_millis, 0) / cpu_total
    mem_used = max(node.total_memory_mb - node.available_memory_mb, 0) / mem_total
    return max(cpu_used, mem_used)
