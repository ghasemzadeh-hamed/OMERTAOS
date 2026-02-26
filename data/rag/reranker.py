"""Simple reranking helpers for RAG."""
from __future__ import annotations


def rerank_by_score(documents: list[dict[str, object]]) -> list[dict[str, object]]:
    return sorted(documents, key=lambda item: float(item.get("score") or 0.0), reverse=True)

__all__ = ["rerank_by_score"]
