"""Utilities for lightweight RAG demos backed by Qdrant."""

from .qdrant_client import (
    get_qdrant_client,
    ensure_collection,
    collection_exists,
    list_collections,
    VECTOR_SIZE,
)
from .ingest import chunk_text, embed_text, ingest_documents, search_documents

__all__ = [
    "get_qdrant_client",
    "ensure_collection",
    "collection_exists",
    "list_collections",
    "VECTOR_SIZE",
    "chunk_text",
    "embed_text",
    "ingest_documents",
    "search_documents",
]
