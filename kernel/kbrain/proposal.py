from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4


class ProposalStatus(str, Enum):
    """Lifecycle states for kernel proposals."""

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    APPLIED = "APPLIED"
    ROLLED_BACK = "ROLLED_BACK"
    EXPIRED = "EXPIRED"


@dataclass
class AuditEvent:
    action: str
    actor: str
    timestamp: datetime
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuditLog:
    created_by: str
    trace_id: str = field(default_factory=lambda: f"trace-{uuid4()}")
    approved_by: Optional[str] = None
    applied_by: Optional[str] = None
    rejected_by: Optional[str] = None
    history: List[AuditEvent] = field(default_factory=list)

    def record(self, action: str, actor: str, **details: Any) -> None:
        event = AuditEvent(action=action, actor=actor, timestamp=datetime.now(timezone.utc), details=details)
        self.history.append(event)


@dataclass
class Scope:
    type: str
    keys: List[str]
    target: str


@dataclass
class Change:
    key: str
    from_value: Any
    to_value: Any


@dataclass
class CanaryConfig:
    percent: int
    granularity: str


@dataclass
class KPIGuard:
    degrade_threshold_pct: float


@dataclass
class KernelProposal:
    proposal_id: str
    source: str
    scope: Scope
    changes: List[Change]
    ttl_seconds: int
    canary: CanaryConfig
    risk_score: float
    expected_impact: Dict[str, float]
    kpi_guard: KPIGuard
    audit: AuditLog
    status: ProposalStatus = ProposalStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    before_metrics: Optional[Dict[str, float]] = None
    after_metrics: Optional[Dict[str, float]] = None
    rollback_reason: Optional[str] = None
    canary_plan: Optional[Dict[str, Any]] = None
    canary_observation: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        if self.ttl_seconds < 0:
            raise ValueError("ttl_seconds must be non-negative")
        self.expires_at = self.created_at + timedelta(seconds=self.ttl_seconds)
        self.audit.record("submitted", self.audit.created_by, status=self.status.value)

    def _touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        data["created_at"] = self.created_at.isoformat()
        data["updated_at"] = self.updated_at.isoformat()
        data["expires_at"] = self.expires_at.isoformat() if self.expires_at else None
        data["changes"] = [
            {"key": change.key, "from": change.from_value, "to": change.to_value}
            for change in self.changes
        ]
        data["audit"] = {
            "created_by": self.audit.created_by,
            "approved_by": self.audit.approved_by,
            "applied_by": self.audit.applied_by,
            "rejected_by": self.audit.rejected_by,
            "trace_id": self.audit.trace_id,
            "history": [
                {
                    "action": event.action,
                    "actor": event.actor,
                    "timestamp": event.timestamp.isoformat(),
                    "details": event.details,
                }
                for event in self.audit.history
            ],
        }
        return data

    def mark_approved(self, actor: str) -> None:
        if self.status not in {ProposalStatus.PENDING}:
            raise ValueError("proposal must be PENDING to approve")
        self.status = ProposalStatus.APPROVED
        self.audit.approved_by = actor
        self.audit.record("approved", actor, status=self.status.value)
        self._touch()

    def mark_rejected(self, actor: str, reason: str) -> None:
        if self.status not in {ProposalStatus.PENDING, ProposalStatus.APPROVED}:
            raise ValueError("proposal cannot be rejected in current state")
        self.status = ProposalStatus.REJECTED
        self.audit.rejected_by = actor
        self.rollback_reason = reason
        self.audit.record("rejected", actor, status=self.status.value, reason=reason)
        self._touch()

    def mark_expired(self) -> None:
        if self.status in {ProposalStatus.APPLIED, ProposalStatus.ROLLED_BACK, ProposalStatus.REJECTED}:
            return
        self.status = ProposalStatus.EXPIRED
        self.audit.record("expired", "safekeeper", status=self.status.value)
        self._touch()

    def mark_applied(self, actor: str, before: Dict[str, float], after: Dict[str, float]) -> None:
        if self.status != ProposalStatus.APPROVED:
            raise ValueError("proposal must be APPROVED to apply")
        self.status = ProposalStatus.APPLIED
        self.before_metrics = before
        self.after_metrics = after
        self.audit.applied_by = actor
        self.audit.record("applied", actor, status=self.status.value)
        self._touch()

    def mark_rolled_back(self, actor: str, reason: str, observed: Optional[Dict[str, float]] = None) -> None:
        self.status = ProposalStatus.ROLLED_BACK
        if observed is not None:
            self.after_metrics = observed
        self.rollback_reason = reason
        self.audit.record("rolled_back", actor, status=self.status.value, reason=reason)
        self._touch()


def build_proposal(payload: Dict[str, Any]) -> KernelProposal:
    scope_data = payload.get("scope", {})
    change_data = payload.get("changes", [])
    audit_data = payload.get("audit", {})

    scope = Scope(
        type=scope_data.get("type", "unknown"),
        keys=list(scope_data.get("keys", [])),
        target=scope_data.get("target", "node"),
    )
    changes = [
        Change(key=item.get("key", ""), from_value=item.get("from"), to_value=item.get("to"))
        for item in change_data
    ]
    canary_data = payload.get("canary", {})
    canary = CanaryConfig(
        percent=int(canary_data.get("percent", 0)),
        granularity=canary_data.get("granularity", "node"),
    )
    kpi_data = payload.get("kpi_guard", {})
    guard = KPIGuard(degrade_threshold_pct=float(kpi_data.get("degrade_threshold_pct", 0)))
    audit = AuditLog(created_by=audit_data.get("created_by", payload.get("source", "unknown")))
    proposal = KernelProposal(
        proposal_id=payload.get("proposal_id"),
        source=payload.get("source", "unknown"),
        scope=scope,
        changes=changes,
        ttl_seconds=int(payload.get("ttl_seconds", 0)),
        canary=canary,
        risk_score=float(payload.get("risk_score", 0.0)),
        expected_impact={str(k): float(v) for k, v in (payload.get("expected_impact") or {}).items()},
        kpi_guard=guard,
        audit=audit,
    )
    return proposal
