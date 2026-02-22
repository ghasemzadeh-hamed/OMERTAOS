"""LatentBox-backed catalog loader and sync helpers."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable, List

import yaml
from pydantic import BaseModel, Field, ValidationError

from os.control.os.core.logger import get_logger
from os.control.os.recommendations.store import ToolResourceRecord, ToolResourceStore

LOGGER = get_logger(__name__)
FEATURE_LATENTBOX = os.getenv("FEATURE_LATENTBOX_RECOMMENDATIONS", "1") in {"1", "true", "TRUE"}


class LatentboxToolEntry(BaseModel):
    id: str
    name: str
    category: str
    url: str
    description: str | None = None
    tags: List[str] = Field(default_factory=list)
    scenarios: List[str] = Field(default_factory=list)
    capabilities: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    source: str = "latentbox"


def _load_yaml(path: Path) -> Iterable[dict]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
            tools = data.get("tools") if isinstance(data, dict) else None
            return tools if isinstance(tools, list) else []
    except FileNotFoundError:
        LOGGER.warning("latentbox catalog not found", extra={"path": str(path)})
        return []
    except yaml.YAMLError as exc:
        LOGGER.warning("invalid latentbox catalog yaml", extra={"path": str(path), "error": str(exc)})
        return []


def load_latentbox_catalog(root: Path | None = None) -> List[ToolResourceRecord]:
    catalog_root = Path(root) if root else Path(os.getenv("AION_LATENTBOX_DIR", "config/latentbox"))
    catalog_path = catalog_root / "tools.yaml"
    records: List[ToolResourceRecord] = []
    for raw in _load_yaml(catalog_path):
        if not isinstance(raw, dict):
            continue
        try:
            entry = LatentboxToolEntry(**raw)
        except ValidationError as exc:
            LOGGER.warning("invalid latentbox entry", extra={"error": str(exc), "entry": raw})
            continue
        record = ToolResourceRecord(
            id=entry.id,
            name=entry.name,
            category=entry.category,
            url=entry.url,
            description=entry.description,
            tags=entry.tags,
            source=entry.source,
            scenarios=entry.scenarios,
            capabilities=entry.capabilities,
            constraints=entry.constraints,
        )
        records.append(record)
    return records


async def sync_latentbox_catalog(store: ToolResourceStore, root: Path | None = None) -> List[ToolResourceRecord]:
    if not FEATURE_LATENTBOX:
        return []
    records = load_latentbox_catalog(root)
    if not records:
        LOGGER.info("latentbox catalog empty", extra={"path": str(root) if root else "default"})
        return []
    stored = await store.upsert_many(records)
    LOGGER.info("latentbox catalog synced", extra={"count": len(stored)})
    return stored
