"""Reinforcement learning agent placeholder for process decisions."""

from typing import Any, Dict, List


class TabularRLAgent:
    """Minimal Q-learning agent for discrete state-action spaces."""

    def __init__(self, actions: List[str], learning_rate: float = 0.1, discount: float = 0.9):
        self.actions = actions
        self.learning_rate = learning_rate
        self.discount = discount
        self.q_values: Dict[tuple, float] = {}

    def select_action(self, state: Any, epsilon: float = 0.1) -> str:
        """Epsilon-greedy action selection."""
        if state is None or not self.actions:
            raise ValueError("State and actions must be defined")
        from random import choice, random

        if random() < epsilon:
            return choice(self.actions)
        return max(self.actions, key=lambda action: self.q_values.get((state, action), 0.0))

    def update(self, state: Any, action: str, reward: float, next_state: Any) -> None:
        """Update Q-values using the standard Q-learning rule."""
        best_next = max(self.actions, key=lambda act: self.q_values.get((next_state, act), 0.0))
        target = reward + self.discount * self.q_values.get((next_state, best_next), 0.0)
        current = self.q_values.get((state, action), 0.0)
        self.q_values[(state, action)] = current + self.learning_rate * (target - current)
