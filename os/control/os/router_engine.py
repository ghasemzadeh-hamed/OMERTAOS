from typing import Any, Dict
import random
from os.control.os.config import get_settings
from os.control.os.models import RouterDecision, Task
from os.control.os.policy import policy_store
from os.control.aionos_profiles import get_profile


class DecisionEngine:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.profile_name, self.profile_config = get_profile()

    def decide(self, task: Task) -> RouterDecision:
        policies = policy_store.get_policy("intents.yml")
        intent_cfg = policies.get(task.intent, {})
        router_cfg = self.profile_config.get("features", {}).get("router", {})
        default_mode = router_cfg.get("default_mode", "auto")
        privacy_mode = task.sla.get("privacy") or intent_cfg.get("privacy", "allow-api")
        candidates = intent_cfg.get("candidates", ["local", "api", "hybrid"])
        if default_mode in {"local", "local-only"} or privacy_mode == "local-only":
            route = "local"
            reason = "profile_local" if default_mode != "auto" else "privacy_enforced"
        else:
            if task.preferred_engine != "auto":
                route = task.preferred_engine
                reason = "preferred_engine"
            elif default_mode in {"hybrid", "remote-canary"}:
                route = "hybrid" if default_mode == "hybrid" else "api"
                reason = "profile_default"
            else:
                route = random.choice(candidates)
                reason = "policy_randomized"
        tier = intent_cfg.get("tiers_allowed", ["tier0"])[0]
        if task.sla.get("budget_usd", self.settings.default_budget) > self.settings.hard_budget_cap:
            route = "hybrid"
            reason = "budget_cap"
            tier = "tier1"
        return RouterDecision(route=route, reason=reason, chosen_by="policy", tier=tier)


decision_engine = DecisionEngine()
