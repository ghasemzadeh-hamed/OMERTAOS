"""Embedding helpers for data-plane RAG."""
from __future__ import annotations

import hashlib

from data.vector.qdrant_client import VECTOR_SIZE


def _hash_bytes(value: str) -> bytes:
    return hashlib.sha256(value.encode("utf-8")).digest()


def embed_text(text: str, dims: int = VECTOR_SIZE) -> list[float]:
    """Create deterministic pseudo-embeddings without heavy ML dependencies."""
    digest = _hash_bytes(text)
    vector: list[float] = []
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

__all__ = ["embed_text"]
