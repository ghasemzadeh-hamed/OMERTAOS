"""Ingestion helpers for centralized RAG data plane."""
from __future__ import annotations

import uuid
from typing import Sequence

from qdrant_client import QdrantClient
from qdrant_client.http import models as rest

from data.rag.embedding import embed_text
from data.vector.qdrant_client import ensure_collection


def chunk_text(text: str, chunk_size: int = 600, overlap: int = 120) -> list[str]:
    words = text.split()
    if not words:
        return []
    chunks: list[str] = []
    step = max(1, chunk_size - overlap)
    for start in range(0, len(words), step):
        window = words[start : start + chunk_size]
        if window:
            chunks.append(" ".join(window))
    return chunks


def ingest_documents(
    client: QdrantClient,
    collection: str,
    texts: Sequence[str],
    metadata: dict[str, str] | None = None,
) -> int:
    ensure_collection(client, collection)
    points: list[rest.PointStruct] = []
    for text in texts:
        clean = text.strip()
        if not clean:
            continue
        payload: dict[str, str] = {"text": clean}
        if metadata:
            payload.update(metadata)
        points.append(rest.PointStruct(id=uuid.uuid4().hex, vector=embed_text(clean), payload=payload))
    if not points:
        return 0
    client.upsert(collection_name=collection, points=points)
    return len(points)

__all__ = ["chunk_text", "ingest_documents"]
