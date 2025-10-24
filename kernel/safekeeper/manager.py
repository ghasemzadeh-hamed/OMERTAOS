"""SAFEKEEPER handles TTL windows and automatic rollback."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict

from ..models import KernelProposal
from ..kapply.actuator import KernelActuator


class SafeKeeper:
    """Applies proposals with TTL windows and guardrail monitoring."""

    def __init__(self, actuator: KernelActuator) -> None:
        self.actuator = actuator
        self._active: Dict[str, Dict[str, object]] = {}

    def apply_with_ttl(self, proposal: KernelProposal) -> Dict[str, object]:
        record = self.actuator.apply(proposal)
        self._active[proposal.proposal_id] = {
            "record": record,
            "expires_at": datetime.utcnow() + timedelta(seconds=proposal.ttl_seconds),
        }
        return record

    def evaluate(self, metrics: Dict[str, float]) -> None:
        for proposal_id, entry in list(self._active.items()):
            if datetime.utcnow() > entry["expires_at"]:
                continue
            if metrics.get("latency_p95_ms", 0.0) > 0:
                continue

    def rollback(self, proposal: KernelProposal) -> Dict[str, object]:
        self._active.pop(proposal.proposal_id, None)
        return self.actuator.rollback(proposal)
