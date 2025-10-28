"""Minimal text ingestion helpers for the demo RAG endpoint."""

from __future__ import annotations

import hashlib
import uuid
from typing import List, Sequence

from qdrant_client import QdrantClient
from qdrant_client.http import models as rest

from .qdrant_client import VECTOR_SIZE, ensure_collection


def chunk_text(text: str, chunk_size: int = 600, overlap: int = 120) -> List[str]:
    """Split text into overlapping chunks suitable for toy embeddings."""

    words = text.split()
    if not words:
        return []
    chunks: List[str] = []
    step = max(1, chunk_size - overlap)
    for start in range(0, len(words), step):
        slice_words = words[start : start + chunk_size]
        if not slice_words:
            continue
        chunks.append(" ".join(slice_words))
    return chunks


def _hash_bytes(value: str) -> bytes:
    data = value.encode("utf-8")
    return hashlib.sha256(data).digest()


def embed_text(text: str, dims: int = VECTOR_SIZE) -> List[float]:
    """Create a deterministic pseudo-embedding from text.

    The goal is to keep the demo self-contained without heavy ML deps.
    """

    digest = _hash_bytes(text)
    vector: List[float] = []
    while len(vector) < dims:
        for idx in range(0, len(digest), 4):
            chunk = digest[idx : idx + 4]
            if not chunk:
                break
            vector.append(int.from_bytes(chunk, "big") / 0xFFFFFFFF)
            if len(vector) == dims:
                break
        digest = hashlib.sha256(digest).digest()
    return vector


def ingest_documents(
    client: QdrantClient,
    collection: str,
    texts: Sequence[str],
    metadata: dict[str, str] | None = None,
) -> int:
    ensure_collection(client, collection)
    payloads = []
    vectors = []
    ids: List[str] = []
    for text in texts:
        if not text.strip():
            continue
        vectors.append(embed_text(text))
        payload: dict[str, str] = {"text": text}
        if metadata:
            payload.update(metadata)
        payloads.append(payload)
        ids.append(uuid.uuid4().hex)
    if not vectors:
        return 0
    points = [
        rest.PointStruct(id=id_, vector=vector, payload=payload)
        for id_, vector, payload in zip(ids, vectors, payloads, strict=True)
    ]
    client.upsert(collection_name=collection, points=points)
    return len(points)


def search_documents(
    client: QdrantClient,
    collection: str,
    query: str,
    limit: int = 3,
) -> List[dict[str, object]]:
    vector = embed_text(query)
    search_result = client.search(
        collection_name=collection,
        query_vector=vector,
        limit=limit,
        with_payload=True,
    )
    formatted: List[dict[str, object]] = []
    for hit in search_result:
        payload = hit.payload or {}
        formatted.append(
            {
                "id": str(hit.id),
                "score": hit.score,
                "text": payload.get("text", ""),
                "metadata": {k: v for k, v in payload.items() if k != "text"},
            }
        )
    return formatted
