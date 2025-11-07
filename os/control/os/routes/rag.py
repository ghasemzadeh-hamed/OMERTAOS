"""Demo RAG endpoints for quick-start flows."""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field

from os.control.os.rag import (
    chunk_text,
    collection_exists,
    ensure_collection,
    get_qdrant_client,
    ingest_documents,
    list_collections,
    search_documents,
)

router = APIRouter(prefix="/rag", tags=["rag"])


class QueryBody(BaseModel):
    collection: str = Field(..., description="Collection to search")
    query: str = Field(..., description="Free-text query")
    limit: int = Field(default=3, ge=1, le=20)


@router.get("/collections")
def collections() -> dict[str, List[str]]:
    client = get_qdrant_client()
    return {"collections": list(list_collections(client))}


@router.post("/ingest")
async def ingest(  # type: ignore[override]
    col: str = Form(..., description="Collection name"),
    files: List[UploadFile] | None = File(default=None, description="Text/Markdown files"),
    text: str | None = Form(default=None, description="Ad-hoc text input"),
) -> dict[str, object]:
    client = get_qdrant_client()
    ensure_collection(client, col)

    total_chunks = 0
    file_summaries: List[dict[str, object]] = []

    if files:
        for upload in files:
            raw_bytes = await upload.read()
            try:
                decoded = raw_bytes.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise HTTPException(400, f"{upload.filename}: invalid UTF-8") from exc
            chunks = chunk_text(decoded)
            inserted = ingest_documents(
                client,
                col,
                chunks,
                metadata={"source": upload.filename or "upload"},
            )
            total_chunks += inserted
            file_summaries.append({"file": upload.filename, "chunks": inserted})

    if text:
        inline_chunks = chunk_text(text)
        total_chunks += ingest_documents(client, col, inline_chunks, metadata={"source": "inline"})

    if not total_chunks:
        raise HTTPException(400, "no ingestible content provided")

    return {
        "collection": col,
        "ingested_chunks": total_chunks,
        "files": file_summaries,
    }


@router.post("/query")
def query(body: QueryBody) -> dict[str, object]:
    client = get_qdrant_client()
    if not collection_exists(client, body.collection):
        raise HTTPException(404, "collection not found")
    results = search_documents(client, body.collection, body.query, limit=body.limit)
    return {"results": results}
