from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _registry_root(root: str | Path | None = None) -> Path:
    return Path(root) if root else _repo_root() / "ai_registry"


def load_registry_lock(root: str | Path | None = None) -> dict[str, Any]:
    lock_path = _registry_root(root) / "registry.lock.json"
    with lock_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def get_model(provider: str, model: str, root: str | Path | None = None) -> dict[str, Any]:
    model_path = _registry_root(root) / "models" / provider / f"{model}.yaml"
    with model_path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def get_agent(agent_name: str, root: str | Path | None = None) -> dict[str, Any]:
    agent_path = _registry_root(root) / "algorithms" / agent_name
    if agent_path.with_suffix(".yaml").exists():
        with agent_path.with_suffix(".yaml").open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle) or {}
    for candidate in agent_path.rglob("*.yaml"):
        with candidate.open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle) or {}
    raise FileNotFoundError(f"agent '{agent_name}' not found in registry")


def list_agents(root: str | Path | None = None) -> list[str]:
    algorithms = _registry_root(root) / "algorithms"
    return sorted([p.stem for p in algorithms.rglob("*.yaml")])


def resolve_hosted_model(alias: str, root: str | Path | None = None) -> dict[str, Any]:
    lock = load_registry_lock(root)
    models = lock.get("models", [])
    for item in models:
        if item.get("name") == alias or item.get("id") == alias:
            return item
    raise KeyError(f"model alias '{alias}' not found in registry lock")
