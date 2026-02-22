from __future__ import annotations

import subprocess
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel, Field

from os.control.os.config import get_settings
from os.control.os.models.registry import ModelRegistry, PrivacyLevel, get_model_registry

router = APIRouter()


class ModelSelectionRequest(BaseModel):
    intent: str = Field(..., description="Intent name to satisfy")
    privacy: PrivacyLevel = Field(
        PrivacyLevel.ALLOW_API,
        description="Requested privacy policy for the inference",
    )
    preferred: List[str] = Field(
        default_factory=list,
        description="Optional explicit set of model names to consider",
    )
    require_healthy: bool = Field(
        default=True,
        description="Skip health probing when false (useful for dry-runs)",
    )


class InstallModelRequest(BaseModel):
    engine: str = Field(..., examples=["ollama", "vllm"])
    model: str = Field(..., description="Model identifier to install")
    display_name: Optional[str] = None
    privacy: PrivacyLevel = PrivacyLevel.LOCAL_ONLY
    intents: List[str] = Field(default_factory=list)
    endpoint: Optional[str] = Field(
        default=None, description="Custom health endpoint to register"
    )


def _ensure_registry() -> ModelRegistry:
    return get_model_registry()


@router.get("/models", response_model=list[dict[str, object]])
async def list_models(registry: ModelRegistry = Depends(_ensure_registry)):
    return registry.list_models()


@router.post("/models/select", response_model=dict[str, object])
async def select_model(
    payload: ModelSelectionRequest,
    registry: ModelRegistry = Depends(_ensure_registry),
):
    record = await registry.select_model(
        payload.intent,
        requested_privacy=payload.privacy,
        preferred=payload.preferred,
        require_healthy=payload.require_healthy,
    )
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="no model")
    return record.to_dict()


@router.post("/models/reload")
async def reload_models(registry: ModelRegistry = Depends(_ensure_registry)):
    registry.reload()
    return {
        "status": "reloaded",
        "defaults": registry.defaults,
        "count": len(registry.list_models()),
    }


@router.get("/models/{model_name}/health")
async def model_health(
    model_name: str,
    registry: ModelRegistry = Depends(_ensure_registry),
):
    try:
        payload = await registry.ensure_health(model_name)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return payload


@router.post("/models/install")
async def install_model(
    payload: InstallModelRequest,
    background: BackgroundTasks,
    registry: ModelRegistry = Depends(_ensure_registry),
):
    settings = get_settings()
    script_path = Path("scripts/install_llm.sh").resolve()
    if not script_path.exists():
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="install script missing")

    command = [
        "bash",
        str(script_path),
        payload.engine,
        payload.model,
        "--privacy",
        payload.privacy.value,
    ]

    if payload.display_name:
        command.extend(["--display", payload.display_name])
    if payload.intents:
        command.extend(["--intents", ",".join(payload.intents)])
    if payload.endpoint:
        command.extend(["--endpoint", payload.endpoint])
    command.extend(["--policies", str(Path(settings.policies_directory).resolve())])

    def _runner() -> None:
        subprocess.run(command, check=True)
        registry.reload()

    background.add_task(_runner)
    return {
        "status": "scheduled",
        "engine": payload.engine,
        "model": payload.model,
    }
