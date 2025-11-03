"""Dynamic policy evaluation for routing and scheduling decisions."""
from __future__ import annotations

import json
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class PolicyResult:
    """Outcome returned by policy evaluation."""

    allowed: bool
    reason: str
    tags: List[str]
    requires_supervision: bool
    risk_score: float


class PolicyEngine:
    """Loads policy definitions and evaluates requests against them."""

    def __init__(self, policy_path: Path) -> None:
        self._policy_path = policy_path
        self._lock = threading.Lock()
        self._policies = self._load_policies()
        self._rate_counters: Dict[str, List[float]] = {}

    def _load_policies(self) -> Dict[str, Any]:
        if not self._policy_path.exists():
            return {}
        with self._policy_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def reload(self) -> None:
        """Reload policy definitions from disk."""
        with self._lock:
            self._policies = self._load_policies()
            self._rate_counters.clear()

    def evaluate(self, intent: str, context: Dict[str, Any]) -> PolicyResult:
        """Evaluate policies for a given intent and request context."""
        with self._lock:
            rules = self._policies.get(intent) or {}
            global_rules = self._policies.get("__default__", {})
            merged = {**global_rules, **rules}

            tags = list(merged.get("tags", []))
            allowed = merged.get("default", True)
            requires_supervision = merged.get("supervision", False)
            risk_threshold = float(merged.get("max_risk", 1.0))
            risk_score = float(context.get("risk_score", 0.0))

            roles = set(context.get("roles", []))
            deny_roles = set(merged.get("deny_roles", []))
            allow_roles = set(merged.get("allow_roles", []))
            scopes_required = set(merged.get("required_scopes", []))
            scopes = set(context.get("scopes", []))

            if deny_roles & roles:
                return PolicyResult(False, "role_denied", tags, True, risk_score)
            if allow_roles and not (allow_roles & roles):
                return PolicyResult(False, "missing_role", tags, True, risk_score)
            if scopes_required and not scopes_required.issubset(scopes):
                return PolicyResult(False, "missing_scope", tags, True, risk_score)
            if risk_score > risk_threshold:
                return PolicyResult(False, "risk_threshold_exceeded", tags, True, risk_score)

            blocked_models = set(merged.get("blocked_models", []))
            model = context.get("model")
            if model and model in blocked_models:
                return PolicyResult(False, "model_blocked", tags, True, risk_score)

            limit = merged.get("rate_limit_per_minute")
            if limit:
                now = time.time()
                window_start = now - 60
                bucket = self._rate_counters.setdefault(intent, [])
                bucket[:] = [ts for ts in bucket if ts >= window_start]
                if len(bucket) >= int(limit):
                    return PolicyResult(False, "rate_limited", tags, True, risk_score)
                bucket.append(now)

            return PolicyResult(allowed, "", tags, requires_supervision, risk_score)


__all__ = ["PolicyEngine", "PolicyResult"]
