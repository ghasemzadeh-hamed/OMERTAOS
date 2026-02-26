"""RAG contracts shared across planes."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class Document:
    """Generic retrieved document shape for RAG interfaces."""

    id: str
    text: str
    score: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class RAGEngine(Protocol):
    """Interface for retrieval components."""

    def retrieve(self, query: str, limit: int = 3) -> list[Document]:
        """Retrieve relevant documents for a query."""
