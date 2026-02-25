from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Protocol

import requests

from .config import settings


class ModelRegistryPort(Protocol):
    def get_best_score(self) -> float: ...

    def register_if_better(self, model_path: str, score: float) -> bool: ...


class HTTPModelRegistryClient:
    def get_best_score(self) -> float:
        try:
            response = requests.get(f"{settings.REGISTRY_URL}/models", timeout=10)
            response.raise_for_status()
            models = response.json()
            if not isinstance(models, list):
                return 0.0
            return max((float(model.get("score", 0.0)) for model in models), default=0.0)
        except Exception:
            return 0.0

    def register_if_better(self, model_path: str, score: float) -> bool:
        best = self.get_best_score()
        if score < best + settings.IMPROVEMENT_THRESHOLD:
            return False

        payload: Dict[str, Any] = {
            "name": Path(model_path).name,
            "parent": settings.BASE_MODEL_NAME,
            "path": model_path,
            "score": score,
            "metadata": {"source": "seal-adapter"},
        }
        response = requests.post(f"{settings.REGISTRY_URL}/models", json=payload, timeout=10)
        response.raise_for_status()
        return True
