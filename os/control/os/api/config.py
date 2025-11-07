"""Configuration center endpoints."""
from __future__ import annotations

from collections.abc import Mapping
import copy
import os
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from dotenv import dotenv_values
import yaml

from .security import admin_required, admin_or_devops_required


router = APIRouter(prefix="/api/config", tags=["config"])

_CONFIG_FILE = Path(os.getenv("AION_CONFIG_FILE", "config/aionos.yaml"))
_ENV_FILE = Path(os.getenv("AION_ENV_FILE", ".env"))


SENSITIVE_KEYS = {"KEY", "SECRET", "TOKEN", "PASSWORD"}


def _mask(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {k: _mask(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_mask(item) for item in value]
    if isinstance(value, str):
        upper = value.upper()
        if any(marker in upper for marker in {"SECRET", "TOKEN", "PASSWORD"}):
            return "***" if value else value
    return value


def _mask_keys(payload: Mapping[str, Any]) -> dict[str, Any]:
    masked: dict[str, Any] = {}
    for key, value in payload.items():
        if any(marker in key.upper() for marker in SENSITIVE_KEYS):
            masked[key] = "***" if value else value
        else:
            if isinstance(value, Mapping):
                masked[key] = _mask(value)
            elif isinstance(value, list):
                masked[key] = [_mask(item) for item in value]
            else:
                masked[key] = value
    return masked


def _load_env() -> dict[str, Any]:
    if not _ENV_FILE.exists():
        return {}
    return {k: v for k, v in dotenv_values(_ENV_FILE).items() if v is not None}


def _load_yaml() -> dict[str, Any]:
    if not _CONFIG_FILE.exists():
        return {}
    with _CONFIG_FILE.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="invalid config format")
    return data


def _write_yaml(data: Mapping[str, Any]) -> None:
    _CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with _CONFIG_FILE.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(dict(data), handle, sort_keys=True)


class VectorStoreConfig(BaseModel):
    qdrant_url: str | None = None
    qdrant_api_key: str | None = None
    mongo_dsn: str | None = None


class StorageConfig(BaseModel):
    postgres_dsn: str | None = None
    minio_endpoint: str | None = None
    minio_access_key: str | None = None
    minio_secret_key: str | None = None


class ModelConfig(BaseModel):
    directories: list[str] = Field(default_factory=list)
    default_model: str | None = None


class NetworkConfig(BaseModel):
    api_base_url: str | None = None
    gateway_url: str | None = None
    console_url: str | None = None
    minio_endpoint: str | None = None
    qdrant_endpoint: str | None = None
    tls_cert_path: str | None = None
    tls_key_path: str | None = None


class ConfigDocument(BaseModel):
    model: ModelConfig | None = None
    vector_store: VectorStoreConfig | None = None
    storage: StorageConfig | None = None
    tenancy_mode: str | None = Field(default=None, alias="TENANCY_MODE")
    profile: str | None = Field(default=None, alias="AION_PROFILE")
    metrics_enabled: bool | None = Field(default=None, alias="AION_METRICS_ENABLED")
    metrics_prom_url: str | None = Field(default=None, alias="AION_METRICS_PROM_URL")
    network: NetworkConfig | None = None  # type: ignore[assignment]

    class Config:
        populate_by_name = True


def _merge_effective(env: Mapping[str, Any], overrides: Mapping[str, Any]) -> dict[str, Any]:
    merged = dict(env)
    for key, value in overrides.items():
        if isinstance(value, Mapping) and isinstance(merged.get(key), Mapping):
            merged[key] = _merge_effective(merged[key], value)  # type: ignore[arg-type]
        else:
            merged[key] = value
    return merged


@router.get("")
async def get_config(principal=Depends(admin_or_devops_required())) -> dict[str, Any]:
    env_config = _load_env()
    file_config = _load_yaml()
    effective = _merge_effective(env_config, file_config)
    return {
        "env": _mask_keys(env_config),
        "file": _mask_keys(file_config),
        "effective": _mask_keys(effective),
    }


@router.post("")
async def update_config(
    document: ConfigDocument,
    principal=Depends(admin_required()),
) -> dict[str, Any]:
    existing = _load_yaml()
    payload = {k: v for k, v in document.model_dump(by_alias=True, exclude_none=True).items()}
    merged = copy.deepcopy(existing)
    for key, value in payload.items():
        merged[key] = value
    _write_yaml(merged)
    return {
        "updated": payload,
        "previous": _mask_keys(existing),
        "effective": _mask_keys(_merge_effective(_load_env(), merged)),
    }


network_router = APIRouter(prefix="/api/network", tags=["network"])


@network_router.get("/config")
async def get_network_config(principal=Depends(admin_or_devops_required())) -> dict[str, Any]:
    file_config = _load_yaml()
    network = file_config.get("network", {})
    return {
        "network": network,
    }


class NetworkUpdate(BaseModel):
    api_base_url: str | None = None
    gateway_url: str | None = None
    console_url: str | None = None
    minio_endpoint: str | None = None
    qdrant_endpoint: str | None = None
    tls_cert_path: str | None = None
    tls_key_path: str | None = None


@network_router.post("/config")
async def update_network_config(
    update: NetworkUpdate,
    principal=Depends(admin_required()),
) -> dict[str, Any]:
    config = _load_yaml()
    network = config.get("network", {})
    network.update(update.model_dump(exclude_none=True))
    config["network"] = network
    _write_yaml(config)
    return {"network": network}


__all__ = ["router", "network_router", "ConfigDocument", "NetworkUpdate"]
