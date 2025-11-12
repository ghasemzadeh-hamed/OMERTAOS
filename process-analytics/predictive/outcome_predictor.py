"""Outcome prediction models."""

from typing import Any, Dict, List


class RuleBasedOutcomePredictor:
    """Predict binary outcomes using simple threshold rules."""

    def __init__(self, thresholds: Dict[str, float]):
        self.thresholds = thresholds

    def predict(self, features: Dict[str, Any]) -> str:
        """Return "success" or "risk" based on configured thresholds."""
        for feature, threshold in self.thresholds.items():
            value = float(features.get(feature, 0.0))
            if value > threshold:
                return "risk"
        return "success"

    @classmethod
    def train(cls, historical_data: List[Dict[str, Any]], target: str) -> "RuleBasedOutcomePredictor":
        """Derive thresholds using average feature values grouped by outcome."""
        groups: Dict[str, Dict[str, float]] = {}
        counts: Dict[str, int] = {}
        for row in historical_data:
            label = row[target]
            counts[label] = counts.get(label, 0) + 1
            feature_store = groups.setdefault(label, {})
            for key, value in row.items():
                if key == target:
                    continue
                feature_store[key] = feature_store.get(key, 0.0) + float(value)
        if not groups:
            return cls({})
        success_profile = {k: v / counts.get("success", 1) for k, v in groups.get("success", {}).items()}
        risk_profile = {k: v / counts.get("risk", 1) for k, v in groups.get("risk", {}).items()}
        thresholds = {
            feature: (risk_profile.get(feature, 0.0) + success_profile.get(feature, 0.0)) / 2
            for feature in set(success_profile) | set(risk_profile)
        }
        return cls(thresholds)
