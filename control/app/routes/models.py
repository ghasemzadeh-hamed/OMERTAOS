"""Model registry endpoints."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..config import get_settings


class ModelEntry(BaseModel):
    name: str
    provider: str
    endpoint: str
    tier: str = "local"
    privacy: str = "allow-api"


settings = get_settings()
registry_path = Path(settings.models_directory) / "registry.json"
registry_path.parent.mkdir(parents=True, exist_ok=True)

router = APIRouter(prefix="/v1/models", tags=["models"])


def _load_registry() -> Dict[str, object]:
    if registry_path.exists():
        import json

        return json.loads(registry_path.read_text())
    return {"models": []}


def _persist_registry(payload: Dict[str, object]) -> None:
    import json

    registry_path.write_text(json.dumps(payload, indent=2))


@router.get("")
def list_models():
    return _load_registry()


@router.post("")
def register_model(entry: ModelEntry):
    registry = _load_registry()
    models: List[Dict[str, object]] = registry.setdefault("models", [])  # type: ignore
    models = [model for model in models if model["name"] != entry.name]
    models.append(entry.dict())
    registry["models"] = models
    _persist_registry(registry)
    return {"status": "registered", "model": entry.dict()}


@router.delete("/{name}")
def delete_model(name: str):
    registry = _load_registry()
    models: List[Dict[str, object]] = registry.get("models", [])  # type: ignore
    updated = [model for model in models if model.get("name") != name]
    if len(updated) == len(models):
        raise HTTPException(status_code=404, detail="model not found")
    registry["models"] = updated
    _persist_registry(registry)
    return {"status": "deleted", "name": name}
