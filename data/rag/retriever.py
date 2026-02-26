"""Retrieval helpers for centralized RAG data plane."""
from __future__ import annotations

from qdrant_client import QdrantClient

from data.rag.embedding import embed_text


def search_documents(
    client: QdrantClient,
    collection: str,
    query: str,
    limit: int = 3,
) -> list[dict[str, object]]:
    vector = embed_text(query)
    results = client.search(
        collection_name=collection,
        query_vector=vector,
        limit=limit,
        with_payload=True,
    )
    return [
        {
            "id": str(hit.id),
            "score": hit.score,
            "text": (hit.payload or {}).get("text", ""),
            "metadata": {k: v for k, v in (hit.payload or {}).items() if k != "text"},
        }
        for hit in results
    ]

__all__ = ["search_documents"]
