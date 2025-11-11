"""Decision engine combining predictive and prescriptive signals."""

from typing import Any, Dict, List


class DecisionEngine:
    """Aggregate signals and propose concrete actions."""

    def __init__(self, optimizer, rl_agent):
        self.optimizer = optimizer
        self.rl_agent = rl_agent

    def propose_actions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate actions using optimization and reinforcement learning."""
        decision_space = context.get("decision_space", [])
        if not decision_space:
            return []
        fitness = context.get("fitness", lambda decision: 0.0)
        best_decision = self.optimizer.optimize(decision_space, fitness)
        state = context.get("state")
        action_name = self.rl_agent.select_action(state) if state is not None else best_decision.get("action")
        return [
            {
                "action": action_name,
                "parameters": best_decision,
                "confidence": context.get("confidence", 0.5),
            }
        ]
