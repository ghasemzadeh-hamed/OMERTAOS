"""Shared kernel data models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional
import uuid


class KernelProposalStatus(str, Enum):
    """Lifecycle statuses for kernel proposals."""

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    APPLIED = "APPLIED"
    ROLLED_BACK = "ROLLED_BACK"


@dataclass(slots=True)
class KernelScope:
    """Scope impacted by a kernel change."""

    type: str
    keys: List[str]
    target: str


@dataclass(slots=True)
class KernelChange:
    """Represents a configuration change."""

    key: str
    from_value: str | None
    to_value: str


@dataclass(slots=True)
class KernelGuardrail:
    """Guardrail parameters for proposal safety."""

    degrade_threshold_pct: float


@dataclass(slots=True)
class KernelCanary:
    """Canary configuration."""

    percent: int
    granularity: str


@dataclass(slots=True)
class KernelAudit:
    created_by: str
    approved_by: Optional[str] = None
    trace_id: Optional[str] = None


@dataclass(slots=True)
class KernelProposal:
    """Proposal for applying kernel mutations."""

    scope: KernelScope
    changes: List[KernelChange]
    ttl_seconds: int
    canary: KernelCanary
    risk_score: float
    expected_impact: Dict[str, float]
    kpi_guard: KernelGuardrail
    source: str = "kbrain"
    proposal_id: str = field(default_factory=lambda: f"kp_{uuid.uuid4().hex[:10]}")
    status: KernelProposalStatus = KernelProposalStatus.PENDING
    audit: KernelAudit = field(default_factory=lambda: KernelAudit(created_by="system-kbrain"))
    created_at: datetime = field(default_factory=datetime.utcnow)
    approved_at: Optional[datetime] = None
    applied_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    def approve(self, approver: str) -> None:
        self.status = KernelProposalStatus.APPROVED
        self.audit.approved_by = approver
        self.approved_at = datetime.utcnow()
        self.expires_at = self.approved_at + timedelta(seconds=self.ttl_seconds)

    def reject(self, approver: str) -> None:
        self.status = KernelProposalStatus.REJECTED
        self.audit.approved_by = approver

    def apply(self) -> None:
        self.status = KernelProposalStatus.APPLIED
        self.applied_at = datetime.utcnow()

    def rollback(self) -> None:
        self.status = KernelProposalStatus.ROLLED_BACK

    @property
    def is_expired(self) -> bool:
        return self.expires_at is not None and datetime.utcnow() >= self.expires_at
