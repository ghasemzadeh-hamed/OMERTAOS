from __future__ import annotations

from typing import Dict, List

from ..kbrain.proposal import KernelProposal


class KernelActuator:
    """Sandboxed actuator that only prepares mutation plans."""

    def plan(self, proposal: KernelProposal) -> List[Dict[str, str]]:
        plan: List[Dict[str, str]] = []
        for change in proposal.changes:
            plan.append(
                {
                    "action": "sysctl" if proposal.scope.type == "sysctl" else proposal.scope.type,
                    "key": change.key,
                    "from": str(change.from_value),
                    "to": str(change.to_value),
                }
            )
        return plan

    def apply(self, proposal: KernelProposal) -> List[Dict[str, str]]:
        # The actuator never mutates the kernel directly. It only returns a plan
        # that an administrator can review and execute out-of-band.
        return self.plan(proposal)
