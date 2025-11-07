from __future__ import annotations

import asyncio
import base64
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Literal, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from os.control.os.config import get_settings


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class MemoryProfile(BaseModel):
    name: str
    embedding_model: str = Field(default="text-embedding-3-large")
    chunk_size: int = Field(default=2048, ge=128, le=65536)
    pipeline: List[str] = Field(
        default_factory=lambda: ["chunk", "embed", "store"],
        description="Ordered pipeline stages to apply during ingestion.",
    )
    retention_days: Optional[int] = Field(
        default=None, description="Override for storage lifecycle policies."
    )
    description: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MemoryIngestRequest(BaseModel):
    upload_id: Optional[str] = Field(
        default=None,
        description="Existing upload identifier. If omitted a new upload is created.",
    )
    profile: Literal["shortform", "longform", "code", "images"]
    total_chunks: int = Field(gt=0, description="Total number of chunks expected.")
    chunk_index: int = Field(ge=0, description="Zero-based chunk index.")
    chunk_data: str = Field(
        description="Base64 encoded payload for the chunk. Supports resumable uploads.",
    )
    metadata: Dict[str, Any] = Field(default_factory=dict)
    mime_type: Optional[str] = Field(
        default=None, description="Original content type used for downstream routing."
    )


class MemoryIngestResponse(BaseModel):
    upload_id: str
    state: Literal["pending", "receiving", "ready"]
    received_chunks: int
    total_chunks: int
    bytes_received: int
    percent_complete: float
    checksum: Optional[str] = None


class MemoryStatusResponse(BaseModel):
    uploads: List[MemoryIngestResponse]
    profiles: List[MemoryProfile]


class MemoryUploadManifest(BaseModel):
    upload_id: str
    profile: str
    total_chunks: int
    received_chunks: List[int] = Field(default_factory=list)
    bytes_received: int = 0
    status: Literal["pending", "receiving", "ready"] = "pending"
    created_at: datetime = Field(default_factory=_utc_now)
    updated_at: datetime = Field(default_factory=_utc_now)
    completed_at: Optional[datetime] = None
    checksum: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    mime_type: Optional[str] = None

    def to_response(self) -> MemoryIngestResponse:
        percent = 0.0
        if self.total_chunks:
            percent = round(len(self.received_chunks) / self.total_chunks * 100, 2)
        return MemoryIngestResponse(
            upload_id=self.upload_id,
            state=self.status,
            received_chunks=len(self.received_chunks),
            total_chunks=self.total_chunks,
            bytes_received=self.bytes_received,
            percent_complete=percent,
            checksum=self.checksum,
        )


class MemoryStore:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        self._lock = asyncio.Lock()
        self._profiles_file = self.root / "profiles.json"

    # Manifest helpers -------------------------------------------------
    def _manifest_path(self, upload_id: str) -> Path:
        return self.root / upload_id / "manifest.json"

    def _chunk_path(self, upload_id: str, chunk_index: int) -> Path:
        return self.root / upload_id / "chunks" / f"chunk_{chunk_index:06d}.bin"

    def _load_manifest(self, upload_id: str) -> Optional[MemoryUploadManifest]:
        path = self._manifest_path(upload_id)
        if not path.exists():
            return None
        return MemoryUploadManifest.model_validate_json(path.read_text())

    def _persist_manifest(self, manifest: MemoryUploadManifest) -> None:
        path = self._manifest_path(manifest.upload_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            manifest.model_dump_json(indent=2, exclude_none=True),
            encoding="utf-8",
        )

    # Profile helpers --------------------------------------------------
    def _load_profiles(self) -> List[MemoryProfile]:
        if not self._profiles_file.exists():
            return []
        payload = json.loads(self._profiles_file.read_text(encoding="utf-8"))
        return [MemoryProfile.model_validate(item) for item in payload]

    def _persist_profiles(self, profiles: Iterable[MemoryProfile]) -> None:
        self._profiles_file.write_text(
            json.dumps(
                [profile.model_dump(mode="json", exclude_none=True) for profile in profiles],
                indent=2,
            ),
            encoding="utf-8",
        )

    # Public API -------------------------------------------------------
    async def ingest_chunk(
        self, payload: MemoryIngestRequest
    ) -> MemoryUploadManifest:
        async with self._lock:
            upload_id = payload.upload_id or f"mem-{uuid4()}"
            manifest = self._load_manifest(upload_id)

            if manifest is None:
                manifest = MemoryUploadManifest(
                    upload_id=upload_id,
                    profile=payload.profile,
                    total_chunks=payload.total_chunks,
                    metadata=payload.metadata,
                    mime_type=payload.mime_type,
                )
            else:
                if manifest.total_chunks != payload.total_chunks:
                    raise HTTPException(
                        status_code=409,
                        detail="total_chunks mismatch for existing upload",
                    )
                if manifest.profile != payload.profile:
                    raise HTTPException(
                        status_code=409,
                        detail="profile mismatch for existing upload",
                    )

            if payload.chunk_index >= manifest.total_chunks:
                raise HTTPException(status_code=400, detail="chunk_index out of range")

            chunk_bytes = base64.b64decode(payload.chunk_data)
            chunk_path = self._chunk_path(upload_id, payload.chunk_index)
            chunk_path.parent.mkdir(parents=True, exist_ok=True)
            previous_size = chunk_path.stat().st_size if chunk_path.exists() else None
            chunk_path.write_bytes(chunk_bytes)

            if payload.chunk_index not in manifest.received_chunks:
                manifest.received_chunks.append(payload.chunk_index)
            manifest.received_chunks.sort()

            if previous_size is None:
                manifest.bytes_received += len(chunk_bytes)
            else:
                manifest.bytes_received -= previous_size
                manifest.bytes_received += len(chunk_bytes)

            manifest.status = (
                "ready"
                if len(manifest.received_chunks) == manifest.total_chunks
                else "receiving"
            )
            manifest.updated_at = _utc_now()

            if manifest.status == "ready":
                manifest = await self._finalize_upload(manifest)
            else:
                self._persist_manifest(manifest)

            return manifest

    async def _finalize_upload(self, manifest: MemoryUploadManifest) -> MemoryUploadManifest:
        upload_dir = self._manifest_path(manifest.upload_id).parent
        payload_path = upload_dir / "payload.bin"
        with payload_path.open("wb") as destination:
            for index in manifest.received_chunks:
                chunk_path = self._chunk_path(manifest.upload_id, index)
                destination.write(chunk_path.read_bytes())

        manifest.completed_at = _utc_now()
        manifest.status = "ready"
        manifest.checksum = self._calculate_checksum(payload_path)
        manifest.updated_at = manifest.completed_at
        self._persist_manifest(manifest)
        return manifest

    async def write_profile(self, profile: MemoryProfile) -> MemoryProfile:
        async with self._lock:
            profiles = self._load_profiles()
            existing = {p.name: p for p in profiles}
            existing[profile.name] = profile
            ordered = sorted(existing.values(), key=lambda item: item.name)
            self._persist_profiles(ordered)
            return profile

    async def list_profiles(self) -> List[MemoryProfile]:
        async with self._lock:
            return self._load_profiles()

    async def list_uploads(self) -> List[MemoryUploadManifest]:
        async with self._lock:
            manifests: List[MemoryUploadManifest] = []
            for manifest_path in self.root.glob("*/manifest.json"):
                try:
                    manifests.append(
                        MemoryUploadManifest.model_validate_json(
                            manifest_path.read_text(encoding="utf-8")
                        )
                    )
                except Exception:  # pragma: no cover - defensive guard
                    continue
            manifests.sort(key=lambda item: item.updated_at, reverse=True)
            return manifests

    @staticmethod
    def _calculate_checksum(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()


settings = get_settings()
store = MemoryStore(Path(settings.memory_storage_path))
router = APIRouter(prefix=f"{settings.api_prefix}/memory", tags=["memory"])


@router.post("/ingest", response_model=MemoryIngestResponse)
async def ingest_memory(payload: MemoryIngestRequest):
    manifest = await store.ingest_chunk(payload)

    return manifest.to_response()


@router.get("/status", response_model=MemoryStatusResponse)
async def memory_status(upload_id: Optional[str] = Query(default=None)):
    if upload_id:
        manifest = await store.list_uploads()
        filtered = [item for item in manifest if item.upload_id == upload_id]
        if not filtered:
            raise HTTPException(status_code=404, detail="upload not found")
        profiles = await store.list_profiles()
        return MemoryStatusResponse(
            uploads=[filtered[0].to_response()],
            profiles=profiles,
        )

    manifests = await store.list_uploads()
    profiles = await store.list_profiles()
    return MemoryStatusResponse(
        uploads=[manifest.to_response() for manifest in manifests],
        profiles=profiles,
    )


@router.post("/profile", response_model=MemoryProfile)
async def define_profile(profile: MemoryProfile):
    return await store.write_profile(profile)
