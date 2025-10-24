from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from ..kbrain.proposal import KernelProposal


@dataclass
class CanaryPlan:
    percent: int
    granularity: str
    description: str


class NetDataplane:
    """Models the programmable network dataplane orchestration."""

    def build_canary_plan(self, proposal: KernelProposal) -> CanaryPlan:
        description = (
            f"Apply {proposal.canary.percent}% rollout at {proposal.canary.granularity} "
            f"for scope {proposal.scope.type}:{','.join(proposal.scope.keys)}"
        )
        return CanaryPlan(
            percent=proposal.canary.percent,
            granularity=proposal.canary.granularity,
            description=description,
        )

    def observe_canary(self, proposal: KernelProposal) -> Dict[str, float]:
        """Return pseudo metrics captured during canary execution."""
        # For now reflect expected improvement directly.
        return {metric: delta for metric, delta in proposal.expected_impact.items()}
