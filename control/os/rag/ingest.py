"""Compatibility shim for ``data.rag`` ingestion and retrieval helpers."""
from __future__ import annotations

from data.rag.embedding import embed_text
from data.rag.ingest import chunk_text, ingest_documents
from data.rag.retriever import search_documents

__all__ = ["chunk_text", "embed_text", "ingest_documents", "search_documents"]
