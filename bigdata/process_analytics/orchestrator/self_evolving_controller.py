"""Self-evolving controller orchestrating analytics-driven actions."""

from typing import Any, Dict, List


class SelfEvolvingController:
    """Consume analytics signals and emit OMERTAOS actions."""

    def __init__(self, decision_engine, adapters):
        self.decision_engine = decision_engine
        self.adapters = adapters

    def tick(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Produce and apply actions based on the provided context snapshot."""
        actions = self.decision_engine.propose_actions(context)
        for action in actions:
            self.adapters.apply(action)
        return actions
