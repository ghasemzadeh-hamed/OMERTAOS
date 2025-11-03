"""Routing logic for AI agent intents within the kernel layer."""
from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .governance_hook import GovernanceHook
from .integration_layer import IntegrationLayer
from .policy_engine import PolicyEngine, PolicyResult


@dataclass
class RouteContext:
    """Context shared across routing decisions."""

    user_id: str
    session_id: str
    channel: str
    metadata: Dict[str, Any]
    jwt_claims: Optional[Dict[str, Any]] = None


@dataclass
class RouteDecision:
    """Final decision returned by the router."""

    audit_id: str
    status: str
    intent: str
    confidence: float
    target_queue: str
    selected_agents: List[Dict[str, Any]]
    reason: Optional[str] = None


class LLMHeuristic:
    """Lightweight heuristic that simulates an LLM routing decision."""

    def score(self, intent: str, payload: Dict[str, Any], context: RouteContext) -> float:
        intent_hash = int(hashlib.sha256(intent.encode("utf-8")).hexdigest(), 16) % 100
        payload_weight = len(json.dumps(payload, sort_keys=True)) % 100
        channel_bias = 10 if context.channel.lower() == "voice" else 5
        risk_penalty = int(context.metadata.get("risk_score", 0) * 100)
        confidence = max(0.0, min(1.0, (intent_hash + payload_weight + channel_bias - risk_penalty) / 200))
        return round(confidence, 2)


class AIRouter:
    """Determines which execution targets should receive agent workloads."""

    def __init__(
        self,
        policy_engine: PolicyEngine,
        governance_hook: GovernanceHook,
        integration_layer: IntegrationLayer,
        heuristic: Optional[LLMHeuristic] = None,
    ) -> None:
        self._policy_engine = policy_engine
        self._governance_hook = governance_hook
        self._integration_layer = integration_layer
        self._heuristic = heuristic or LLMHeuristic()

    def route(self, intent: str, payload: Dict[str, Any], context: RouteContext) -> RouteDecision:
        """Route an intent while enforcing policy and governance checks."""
        policy_result = self._policy_engine.evaluate(intent=intent, context=context.metadata)
        audit_id = str(uuid.uuid4())
        if not policy_result.allowed:
            self._governance_hook.record_decision(
                intent=intent,
                context={**context.metadata, "audit_id": audit_id, "status": "denied", "reason": policy_result.reason},
            )
            return RouteDecision(
                audit_id=audit_id,
                status="denied",
                intent=intent,
                confidence=0.0,
                target_queue="",  # no queue when denied
                selected_agents=[],
                reason=policy_result.reason,
            )

        sanitized_payload = self._mask(payload)
        confidence = self._heuristic.score(intent=intent, payload=sanitized_payload, context=context)
        queue = self._select_queue(policy_result=policy_result, context=context, confidence=confidence)

        execution_plan = self._integration_layer.resolve_execution_plan(
            intent=intent,
            payload=sanitized_payload,
            context=context.metadata,
            policy_tags=policy_result.tags,
        )
        selected_agents = execution_plan.get("agents", [])
        decision = RouteDecision(
            audit_id=audit_id,
            status="accepted",
            intent=intent,
            confidence=confidence,
            target_queue=queue,
            selected_agents=selected_agents,
        )

        audit_context = {
            "audit_id": audit_id,
            "intent": intent,
            "queue": queue,
            "confidence": confidence,
            "selected_agents": [agent.get("id") for agent in selected_agents],
            "metadata": context.metadata,
        }
        self._governance_hook.record_decision(intent=intent, context=audit_context)
        return decision

    def health(self) -> Dict[str, str]:
        """Expose a simple health payload for monitoring."""
        return {"status": "ok", "component": "ai_router"}

    def _mask(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        redacted: Dict[str, Any] = {}
        for key, value in payload.items():
            lowered = key.lower()
            if lowered in {"password", "token", "secret", "ssn"}:
                redacted[key] = "***"
            else:
                redacted[key] = value
        return redacted

    def _select_queue(self, policy_result: PolicyResult, context: RouteContext, confidence: float) -> str:
        sla_hint = context.metadata.get("sla", "standard").lower()
        if sla_hint in {"critical", "p0"}:
            return "critical"
        if confidence < 0.4 or policy_result.requires_supervision:
            return "review"
        if sla_hint in {"expedited", "high"}:
            return "priority"
        return "standard"


__all__ = ["AIRouter", "RouteContext", "RouteDecision"]
