import json
from pathlib import Path
from typing import Any, Dict

from .config import get_settings


class PolicyStore:
    def __init__(self) -> None:
        self._settings = get_settings()
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.reload()

    def reload(self) -> None:
        directory = Path(self._settings.policies_directory).resolve()
        data: Dict[str, Dict[str, Any]] = {}
        for filename in ["intents.yml", "policies.yml", "models.yml", "modules.yml"]:
            path = directory / filename
            if not path.exists():
                continue
            import yaml

            with path.open("r", encoding="utf-8") as f:
                data[filename] = yaml.safe_load(f) or {}
        self._cache = data

    def get_policy(self, name: str) -> Dict[str, Any]:
        return self._cache.get(name, {})

    def to_json(self) -> Dict[str, Any]:
        return self._cache

    def update_policies(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        existing = self._cache.get("policies.yml", {})
        merged = {**existing, **payload}
        self._cache["policies.yml"] = merged
        return merged


policy_store = PolicyStore()
