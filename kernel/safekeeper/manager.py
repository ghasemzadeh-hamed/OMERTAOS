from __future__ import annotations

from datetime import datetime, timezone
from threading import Lock
from typing import Dict, Iterable, Optional

from ..kapply.actuator import KernelActuator
from ..kbrain.proposal import KernelProposal, ProposalStatus, build_proposal
from ..kmon.telemetry import TelemetryMonitor
from ..netd.dataplane import NetDataplane
from .policy import KernelPolicyEnforcer


class ProposalLifecycleManager:
    """Coordinates TTL, canaries, and audit lifecycle for proposals."""

    def __init__(
        self,
        telemetry: TelemetryMonitor,
        actuator: KernelActuator,
        dataplane: NetDataplane,
        policy: KernelPolicyEnforcer,
    ) -> None:
        self._telemetry = telemetry
        self._actuator = actuator
        self._dataplane = dataplane
        self._policy = policy
        self._lock = Lock()
        self._proposals: Dict[str, KernelProposal] = {}

    def submit(self, payload: Dict[str, object]) -> KernelProposal:
        proposal = build_proposal(dict(payload))
        self._policy.validate_submission(proposal)
        with self._lock:
            if proposal.proposal_id in self._proposals:
                raise ValueError(f"proposal {proposal.proposal_id} already exists")
            self._proposals[proposal.proposal_id] = proposal
        return proposal

    def list(self, *, status: Optional[Iterable[ProposalStatus]] = None) -> Iterable[KernelProposal]:
        with self._lock:
            for proposal in list(self._proposals.values()):
                self._expire_if_needed(proposal)
            if status is None:
                return list(self._proposals.values())
            status_set = {s for s in status}
            return [p for p in self._proposals.values() if p.status in status_set]

    def get(self, proposal_id: str) -> KernelProposal:
        with self._lock:
            proposal = self._proposals.get(proposal_id)
            if not proposal:
                raise KeyError(proposal_id)
            self._expire_if_needed(proposal)
            return proposal

    def approve(self, proposal_id: str, actor: str) -> KernelProposal:
        with self._lock:
            proposal = self.get(proposal_id)
            self._policy.validate_admin(actor)
            proposal.mark_approved(actor)
            return proposal

    def reject(self, proposal_id: str, actor: str, reason: str) -> KernelProposal:
        with self._lock:
            proposal = self.get(proposal_id)
            self._policy.validate_admin(actor)
            proposal.mark_rejected(actor, reason)
            return proposal

    def apply_now(self, proposal_id: str, actor: str) -> KernelProposal:
        with self._lock:
            proposal = self.get(proposal_id)
            self._policy.validate_admin(actor)
            self._policy.validate_apply(proposal)
            if proposal.status != ProposalStatus.APPROVED:
                raise ValueError("proposal must be approved before application")
            if proposal.audit.approved_by is None:
                raise ValueError("proposal lacks admin approval")
            if proposal.expires_at and datetime.now(timezone.utc) >= proposal.expires_at:
                proposal.mark_expired()
                return proposal
            baseline = self._telemetry.snapshot(proposal)
            projected = self._telemetry.project(proposal, baseline)
            proposal.before_metrics = baseline.metrics
            proposal.after_metrics = projected.metrics
            proposal.canary_plan = self._dataplane.build_canary_plan(proposal).__dict__
            observation = self._dataplane.observe_canary(proposal)
            proposal.canary_observation = observation
            if not self._policy.evaluate_health_guard(proposal, baseline.metrics, projected.metrics):
                proposal.mark_rolled_back(
                    "safekeeper",
                    reason="kpi_guard_threshold",
                    observed={k: baseline.metrics.get(k, 0.0) + v for k, v in observation.items()},
                )
                return proposal
            plan = self._actuator.apply(proposal)
            proposal.mark_applied(actor, baseline.metrics, projected.metrics)
            proposal.canary_plan["actions"] = plan
            return proposal

    def _expire_if_needed(self, proposal: KernelProposal) -> None:
        if proposal.status in {ProposalStatus.EXPIRED, ProposalStatus.REJECTED, ProposalStatus.APPLIED, ProposalStatus.ROLLED_BACK}:
            return
        if proposal.expires_at and datetime.now(timezone.utc) >= proposal.expires_at:
            proposal.mark_expired()


class ProposalFactory:
    """Adapter to expose simple helpers for the API layer."""

    def __init__(self, lifecycle: ProposalLifecycleManager) -> None:
        self._lifecycle = lifecycle

    def submit(self, payload: Dict[str, object]) -> Dict[str, object]:
        proposal = self._lifecycle.submit(payload)
        return proposal.to_dict()

    def list(self, status: Optional[str] = None) -> Iterable[Dict[str, object]]:
        statuses = None
        if status:
            status_values = [s.strip().upper() for s in status.split(",") if s.strip()]
            statuses = [ProposalStatus(value) for value in status_values]
        proposals = self._lifecycle.list(status=statuses)
        return [proposal.to_dict() for proposal in proposals]

    def get(self, proposal_id: str) -> Dict[str, object]:
        proposal = self._lifecycle.get(proposal_id)
        return proposal.to_dict()

    def approve(self, proposal_id: str, actor: str) -> Dict[str, object]:
        proposal = self._lifecycle.approve(proposal_id, actor)
        return proposal.to_dict()

    def reject(self, proposal_id: str, actor: str, reason: str) -> Dict[str, object]:
        proposal = self._lifecycle.reject(proposal_id, actor, reason)
        return proposal.to_dict()

    def apply_now(self, proposal_id: str, actor: str) -> Dict[str, object]:
        proposal = self._lifecycle.apply_now(proposal_id, actor)
        return proposal.to_dict()
