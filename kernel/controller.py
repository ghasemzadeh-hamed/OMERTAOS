"""Kernel orchestration controller orchestrating proposal lifecycle."""

from __future__ import annotations

import json
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Deque, Dict, Iterable, List, Optional

from .models import (
    KernelAudit,
    KernelCanary,
    KernelChange,
    KernelGuardrail,
    KernelProposal,
    KernelProposalStatus,
    KernelScope,
)
from .kmon.collector import SystemTelemetryCollector
from .kbrain.engine import KernelPolicyEngine
from .kapply.actuator import KernelActuator
from .safekeeper.manager import SafeKeeper


class KernelController:
    """Coordinates telemetry, AI proposals, approvals, and safe application."""

    def __init__(
        self,
        policy_path: Path,
        outbound_hook: Optional[callable] = None,
    ) -> None:
        self.policy_path = policy_path
        self.collector = SystemTelemetryCollector()
        self.policy_engine = KernelPolicyEngine(policy_path)
        self.actuator = KernelActuator()
        self.safekeeper = SafeKeeper(self.actuator)
        self._proposals: Dict[str, KernelProposal] = {}
        self._timeline: Deque[str] = deque(maxlen=512)
        self._outbound_hook = outbound_hook

    def _emit(self, topic: str, payload: Dict[str, object]) -> None:
        if self._outbound_hook:
            self._outbound_hook(topic, payload)

    def ingest_metrics(self) -> Dict[str, float]:
        metrics = self.collector.snapshot()
        self._emit("kernel.telemetry", metrics)
        return metrics

    def create_proposal(self) -> KernelProposal:
        metrics = self.ingest_metrics()
        proposal = self.policy_engine.build_proposal(metrics)
        self._proposals[proposal.proposal_id] = proposal
        self._timeline.appendleft(proposal.proposal_id)
        self._emit("kernel.proposal.created", self.serialize_proposal(proposal))
        return proposal

    def submit_external_proposal(self, payload: Dict[str, object]) -> KernelProposal:
        proposal_kwargs = {
            "scope": KernelScope(**payload["scope"]),
            changes=[KernelChange(**change) for change in payload["changes"]],
            ttl_seconds=int(payload["ttl_seconds"]),
            canary=KernelCanary(**payload["canary"]),
            risk_score=float(payload["risk_score"]),
            expected_impact=dict(payload.get("expected_impact", {})),
            kpi_guard=KernelGuardrail(**payload["kpi_guard"]),
            source=str(payload.get("source", "external")),
            audit=KernelAudit(created_by=str(payload.get("created_by", "external"))),
        }
        proposal_id = payload.get("proposal_id")
        if proposal_id:
            proposal_kwargs["proposal_id"] = str(proposal_id)
        proposal = KernelProposal(**proposal_kwargs)
        self._proposals[proposal.proposal_id] = proposal
        self._timeline.appendleft(proposal.proposal_id)
        self._emit("kernel.proposal.received", self.serialize_proposal(proposal))
        return proposal

    def list_proposals(self, status: Optional[str] = None) -> Iterable[KernelProposal]:
        for proposal_id in self._timeline:
            proposal = self._proposals[proposal_id]
            if status and proposal.status.value != status:
                continue
            yield proposal

    def get_proposal(self, proposal_id: str) -> KernelProposal | None:
        return self._proposals.get(proposal_id)

    def approve(self, proposal_id: str, approver: str) -> KernelProposal:
        proposal = self._require_proposal(proposal_id)
        proposal.approve(approver)
        self._emit("kernel.proposal.approved", self.serialize_proposal(proposal))
        return proposal

    def reject(self, proposal_id: str, approver: str) -> KernelProposal:
        proposal = self._require_proposal(proposal_id)
        proposal.reject(approver)
        self._emit("kernel.proposal.rejected", self.serialize_proposal(proposal))
        return proposal

    def apply(self, proposal_id: str) -> KernelProposal:
        proposal = self._require_proposal(proposal_id)
        if proposal.status != KernelProposalStatus.APPROVED:
            raise ValueError("proposal must be approved before applying")
        record = self.safekeeper.apply_with_ttl(proposal)
        self._emit("kernel.proposal.applied", record)
        return proposal

    def expire(self) -> List[KernelProposal]:
        expired: List[KernelProposal] = []
        for proposal in self._proposals.values():
            if proposal.status == KernelProposalStatus.APPLIED and proposal.is_expired:
                proposal.rollback()
                self._emit("kernel.proposal.ttl_expired", self.serialize_proposal(proposal))
                expired.append(proposal)
        return expired

    @staticmethod
    def serialize_proposal(proposal: KernelProposal) -> Dict[str, object]:
        return {
            "proposal_id": proposal.proposal_id,
            "source": proposal.source,
            "scope": {
                "type": proposal.scope.type,
                "keys": proposal.scope.keys,
                "target": proposal.scope.target,
            },
            "changes": [
                {
                    "key": change.key,
                    "from": change.from_value,
                    "to": change.to_value,
                }
                for change in proposal.changes
            ],
            "ttl_seconds": proposal.ttl_seconds,
            "canary": {
                "percent": proposal.canary.percent,
                "granularity": proposal.canary.granularity,
            },
            "risk_score": proposal.risk_score,
            "expected_impact": proposal.expected_impact,
            "kpi_guard": {
                "degrade_threshold_pct": proposal.kpi_guard.degrade_threshold_pct,
            },
            "status": proposal.status.value,
            "audit": {
                "created_by": proposal.audit.created_by,
                "approved_by": proposal.audit.approved_by,
                "trace_id": proposal.audit.trace_id,
            },
            "created_at": proposal.created_at.isoformat(),
            "approved_at": proposal.approved_at.isoformat() if proposal.approved_at else None,
            "applied_at": proposal.applied_at.isoformat() if proposal.applied_at else None,
            "expires_at": proposal.expires_at.isoformat() if proposal.expires_at else None,
        }

    def _require_proposal(self, proposal_id: str) -> KernelProposal:
        proposal = self._proposals.get(proposal_id)
        if not proposal:
            raise KeyError(f"proposal {proposal_id} not found")
        return proposal

    def dump_state(self, destination: Path) -> None:
        data = [self.serialize_proposal(self._proposals[p]) for p in self._timeline]
        destination.write_text(json.dumps(data, indent=2))

    def load_state(self, source: Path) -> None:
        if not source.exists():
            return
        payload = json.loads(source.read_text())
        for proposal_payload in payload:
            proposal = self.submit_external_proposal(proposal_payload)
            proposal.status = KernelProposalStatus(proposal_payload["status"])
            if proposal_payload.get("approved_at"):
                proposal.approved_at = datetime.fromisoformat(proposal_payload["approved_at"])
            if proposal_payload.get("applied_at"):
                proposal.applied_at = datetime.fromisoformat(proposal_payload["applied_at"])
            if proposal_payload.get("expires_at"):
                proposal.expires_at = datetime.fromisoformat(proposal_payload["expires_at"])
