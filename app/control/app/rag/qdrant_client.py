"""Qdrant client helpers for demo RAG flows."""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Iterable

from qdrant_client import QdrantClient
from qdrant_client.http import models as rest

QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")
VECTOR_SIZE = int(os.getenv("AIONOS_RAG_VECTOR_SIZE", "64"))


def _client_kwargs() -> dict[str, str]:
    kwargs: dict[str, str] = {"url": QDRANT_URL}
    if QDRANT_API_KEY:
        kwargs["api_key"] = QDRANT_API_KEY
    return kwargs


@lru_cache(maxsize=1)
def get_qdrant_client() -> QdrantClient:
    """Return a cached Qdrant client instance."""

    return QdrantClient(**_client_kwargs())


def collection_exists(client: QdrantClient, collection_name: str) -> bool:
    try:
        collections = client.get_collections().collections or []
    except Exception:
        return False
    return any(col.name == collection_name for col in collections)


def ensure_collection(
    client: QdrantClient,
    collection_name: str,
    vector_size: int | None = None,
    distance: rest.Distance = rest.Distance.COSINE,
) -> None:
    if collection_exists(client, collection_name):
        return
    client.create_collection(
        collection_name=collection_name,
        vectors_config=rest.VectorParams(size=vector_size or VECTOR_SIZE, distance=distance),
    )


def list_collections(client: QdrantClient) -> Iterable[str]:
    collections = client.get_collections().collections or []
    for collection in collections:
        yield collection.name
