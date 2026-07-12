"""Composable RAG pipeline implementation."""
from __future__ import annotations

from qdrant_client import QdrantClient

from data.rag.reranker import rerank_by_score
from data.rag.retriever import search_documents
from data.interfaces.rag import Document, RAGEngine


class SimpleRAGPipeline(RAGEngine):
    """Minimal RAG pipeline with retrieval + reranking."""

    def __init__(self, client: QdrantClient, collection: str) -> None:
        self._client = client
        self._collection = collection

    def retrieve(self, query: str, limit: int = 3) -> list[Document]:
        raw = search_documents(self._client, self._collection, query, limit=limit)
        ranked = rerank_by_score(raw)
        return [
            Document(
                id=str(item["id"]),
                text=str(item.get("text") or ""),
                score=float(item.get("score") or 0.0),
                metadata=dict(item.get("metadata") or {}),
            )
            for item in ranked
        ]

__all__ = ["SimpleRAGPipeline"]
