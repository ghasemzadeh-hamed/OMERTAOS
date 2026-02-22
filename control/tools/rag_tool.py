"""Lightweight retrieval augmented generation tool."""

from __future__ import annotations

import json
import os
from typing import Any

try:
    from qdrant_client import QdrantClient  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    QdrantClient = None  # type: ignore


class RagSearchTool:
    """Return knowledge snippets from the internal vector store."""

    name = "rag.search"
    desc = "\u062c\u0633\u062a\u062c\u0648\u06cc \u062f\u0627\u0646\u0634 \u062f\u0627\u062e\u0644\u06cc \u0628\u0631 \u0627\u0633\u0627\u0633 \u062a\u0639\u5d4c\u0647\u200c\u0633\u0627\u0632\u06cc \u0648 \u0628\u0631\u062f\u0627\u0631"

    def __init__(self, qdrant_url: str | None = None, collection: str = "docs") -> None:
        self.qdrant_url = qdrant_url or os.getenv("AION_QDRANT_URL", "http://qdrant:6333")
        self.collection = collection
        self._client = None
        if QdrantClient and self.qdrant_url:
            try:
                self._client = QdrantClient(url=self.qdrant_url)
            except Exception:
                self._client = None

    # Placeholder embeddings until the full pipeline is wired in.
    def _fake_embed(self, text: str) -> list[float]:
        return [float((i + 1) * (ord(char) % 7)) for i, char in enumerate(text[:16])]

    def run(self, query: str, top_k: int = 5) -> str:
        if not query.strip():
            return "Query must not be empty."
        if self._client is None:
            return f"[RAG] \u0646\u062a\u0627\u06cc\u062c \u0633\u0627\u062e\u062a\u06af\u06cc \u0628\u0631\u0627\u06cc: {query} (top_k={top_k})"
        try:
            vector = self._fake_embed(query)
            response = self._client.search(
                collection_name=self.collection,
                query_vector=vector,
                limit=top_k,
            )
            payloads: list[dict[str, Any]] = []
            for point in response:
                payload = getattr(point, "payload", {}) or {}
                text = payload.get("text") or payload.get("content")
                payloads.append({
                    "id": getattr(point, "id", None),
                    "score": getattr(point, "score", None),
                    "text": text,
                })
            return json.dumps(payloads, ensure_ascii=False)
        except Exception as exc:
            return f"RAG query failed: {exc}"
