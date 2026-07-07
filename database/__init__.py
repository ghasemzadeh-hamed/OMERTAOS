"""Legacy, lazy compatibility exports for canonical data-plane primitives."""
from __future__ import annotations

from importlib import import_module
from typing import Any


_EXPORTS = {
    "SimpleRAGPipeline": ("data.rag.pipeline", "SimpleRAGPipeline"),
    "chunk_text": ("data.rag.ingest", "chunk_text"),
    "embed_text": ("data.rag.embedding", "embed_text"),
    "ingest_documents": ("data.rag.ingest", "ingest_documents"),
    "search_documents": ("data.rag.retriever", "search_documents"),
}

__all__ = sorted(_EXPORTS)


def __getattr__(name: str) -> Any:
    target = _EXPORTS.get(name)
    if target is None:
        raise AttributeError(name)
    module_name, attribute = target
    value = getattr(import_module(module_name), attribute)
    globals()[name] = value
    return value
