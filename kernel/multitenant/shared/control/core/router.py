from typing import Any, Dict


def decide(mode: str, health: Dict[str, Any]) -> str:
    if mode == "auto":
        if health.get("local_ok"):
            return "local"
        if health.get("api_ok"):
            return "api"
        return "hybrid"
    return mode
