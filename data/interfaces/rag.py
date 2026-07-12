from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class Document:
    id: str
    text: str
    score: float
    metadata: dict[str, object] = field(default_factory=dict)


class RAGEngine(ABC):
    @abstractmethod
    def retrieve(self, query: str, limit: int = 3) -> list[Document]: ...
