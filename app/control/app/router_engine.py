from typing import Any, Dict
import random
from app.control.app.config import get_settings
from app.control.app.models import RouterDecision, Task
from app.control.app.policy import policy_store


class DecisionEngine:
    def __init__(self) -> None:
        self.settings = get_settings()

    def decide(self, task: Task) -> RouterDecision:
        policies = policy_store.get_policy("intents.yml")
        intent_cfg = policies.get(task.intent, {})
        privacy_mode = task.sla.get("privacy") or intent_cfg.get("privacy", "allow-api")
        candidates = intent_cfg.get("candidates", ["local", "api", "hybrid"])
        if privacy_mode == "local-only":
            route = "local"
            reason = "privacy_enforced"
        else:
            route = task.preferred_engine if task.preferred_engine != "auto" else random.choice(candidates)
            reason = "preferred_engine" if task.preferred_engine != "auto" else "policy_randomized"
        tier = intent_cfg.get("tiers_allowed", ["tier0"])[0]
        if task.sla.get("budget_usd", self.settings.default_budget) > self.settings.hard_budget_cap:
            route = "hybrid"
            reason = "budget_cap"
            tier = "tier1"
        return RouterDecision(route=route, reason=reason, chosen_by="policy", tier=tier)


decision_engine = DecisionEngine()
