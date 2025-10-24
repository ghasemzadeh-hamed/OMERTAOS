"""Routes for memory ingestion and profiles."""

from __future__ import annotations

from pathlib import Path
from typing import Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from memory import MemoryManager, MemoryProfile

manager = MemoryManager(Path("/tmp/aion_memory_catalog.json"))
router = APIRouter(prefix="/v1/memory", tags=["memory"])


class ProfileModel(BaseModel):
    name: str
    chunk_size: int
    overlap: int
    embed_model: str


class IngestModel(BaseModel):
    dataset_id: str
    source: str
    profile: str
    metadata: Dict[str, object] = {}


@router.get("/profiles")
def list_profiles():
    return manager.list_profiles()


@router.post("/profile")
def upsert_profile(profile: ProfileModel):
    manager.register_profile(MemoryProfile(profile.name, profile.chunk_size, profile.overlap, profile.embed_model))
    return {"status": "updated", "profile": profile.dict()}


@router.post("/ingest")
def ingest_dataset(payload: IngestModel):
    profile = manager.profiles.get(payload.profile)
    if not profile:
        raise HTTPException(status_code=404, detail="profile not found")
    result = manager.ingest({
        "dataset_id": payload.dataset_id,
        "source": payload.source,
        "profile": profile.to_dict(),
        "metadata": payload.metadata,
    })
    return result


@router.get("/status")
def memory_status():
    return {"datasets": manager.list_datasets(), "profiles": manager.list_profiles()}
