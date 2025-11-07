"""Personal edition kernel bootstrap."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

from .ai_router import AIRouter, RouteContext, RouteDecision
from .governance_hook import GovernanceHook
from .integration_layer import IntegrationLayer
from .policy_engine import PolicyEngine


@dataclass
class PersonalKernelConfig:
    """Configuration for personal mode."""

    policy_path: str
    default_channel: str = "desktop"
    default_roles: Optional[list[str]] = None


class PersonalKernel:
    """Convenience wrapper for personal edition runtime."""

    def __init__(self, config: PersonalKernelConfig, control_client) -> None:
        self._policy_engine = PolicyEngine(policy_path=Path(config.policy_path))
        self._governance = GovernanceHook()
        self._integration = IntegrationLayer(control_client=control_client)
        self._router = AIRouter(
            policy_engine=self._policy_engine,
            governance_hook=self._governance,
            integration_layer=self._integration,
        )
        self._config = config

    def dispatch(self, intent: str, payload: Dict[str, object], user_id: str) -> RouteDecision:
        """Dispatch an intent using the personal kernel defaults."""
        context = RouteContext(
            user_id=user_id,
            session_id=f"session-{user_id}",
            channel=self._config.default_channel,
            metadata={
                "roles": (self._config.default_roles or ["personal"]),
                "mode": "personal",
                "sla": "standard",
            },
        )
        return self._router.route(intent=intent, payload=payload, context=context)


__all__ = ["PersonalKernel", "PersonalKernelConfig"]
