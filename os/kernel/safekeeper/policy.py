from __future__ import annotations

from pathlib import Path
from typing import Dict

from ..kbrain.proposal import KernelProposal, ProposalStatus

import yaml


class KernelPolicyEnforcer:
    """Loads declarative policy for kernel proposals."""

    def __init__(self, policy_path: Path) -> None:
        self._policy_path = policy_path
        self._policy: Dict[str, object] = {}
        self.reload()

    def reload(self) -> None:
        if not self._policy_path.exists():
            self._policy = {}
            return
        with self._policy_path.open("r", encoding="utf-8") as handle:
            self._policy = yaml.safe_load(handle) or {}

    @property
    def data(self) -> Dict[str, object]:
        return self._policy

    def validate_submission(self, proposal: KernelProposal) -> None:
        allowlist = self._policy.get("allowlist", {})
        scope_policy = allowlist.get(proposal.scope.type, {}) if isinstance(allowlist, dict) else {}
        allowed_keys = set(scope_policy.get("keys", [])) if isinstance(scope_policy, dict) else set()
        if allowed_keys and not set(proposal.scope.keys).issubset(allowed_keys):
            raise ValueError("proposal scope keys are not allow-listed")
        limits = self._policy.get("limits", {})
        max_ttl = limits.get("max_ttl_seconds") if isinstance(limits, dict) else None
        if max_ttl is not None and proposal.ttl_seconds > int(max_ttl):
            raise ValueError("proposal ttl exceeds policy limit")
        max_risk = limits.get("max_risk_score") if isinstance(limits, dict) else None
        if max_risk is not None and proposal.risk_score > float(max_risk):
            raise ValueError("proposal risk score exceeds policy limit")

    def validate_admin(self, actor: str) -> None:
        admins = self._policy.get("admins", [])
        if admins and actor not in admins:
            raise PermissionError("actor is not authorized to approve proposals")

    def validate_apply(self, proposal: KernelProposal) -> None:
        apply_policy = self._policy.get("apply", {})
        require_approval = apply_policy.get("require_admin_approval", True) if isinstance(apply_policy, dict) else True
        if require_approval and proposal.status != ProposalStatus.APPROVED:
            raise ValueError("proposal must be approved prior to apply")

    def evaluate_health_guard(self, proposal: KernelProposal, before: Dict[str, float], projected: Dict[str, float]) -> bool:
        threshold = proposal.kpi_guard.degrade_threshold_pct
        for metric, before_value in before.items():
            after_value = projected.get(metric, before_value)
            if before_value == 0:
                continue
            delta_pct = ((after_value - before_value) / before_value) * 100
            if delta_pct > threshold:
                return False
        return True
