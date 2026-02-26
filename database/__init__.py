"""Data-plane RAG primitives."""

from .embedding import embed_text
from .pipeline import SimpleRAGPipeline
from .retriever import search_documents
from .ingest import chunk_text, ingest_documents

__all__ = [
    "SimpleRAGPipeline",
    "chunk_text",
    "embed_text",
    "ingest_documents",
    "search_documents",
]
