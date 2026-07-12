"""Legacy exports; new code imports from data.rag."""

from data.rag.ingest import chunk_text, ingest_documents

__all__ = ["chunk_text", "ingest_documents"]
