"""Session context tracking for agents."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

import httpx


@dataclass
class AgentContext:
    """Holds context metadata for a single agent session."""

    session_id: str
    user_id: str
    data: Dict[str, Any] = field(default_factory=dict)


class VectorStoreClient:
    """Minimal client for interacting with a Qdrant-compatible API."""

    def __init__(self, base_url: str, api_key: Optional[str] = None) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key

    def upsert(self, collection: str, payload: Dict[str, Any]) -> None:
        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        endpoint = f"{self._base_url}/collections/{collection}/points"
        body = {"points": [payload]}
        with httpx.Client(timeout=5.0) as client:
            response = client.put(endpoint, headers=headers, content=json.dumps(body))
            response.raise_for_status()


class ContextManager:
    """Manages agent contexts with in-memory storage and vector persistence."""

    def __init__(self, vector_client: Optional[VectorStoreClient] = None) -> None:
        base_url = os.environ.get("AION_QDRANT_URL", "http://localhost:6333")
        api_key = os.environ.get("AION_QDRANT_API_KEY")
        self._vector_client = vector_client or VectorStoreClient(base_url=base_url, api_key=api_key)
        self._contexts: Dict[str, AgentContext] = {}

    def create(self, session_id: str, user_id: str, initial: Dict[str, Any] | None = None) -> AgentContext:
        ctx = AgentContext(session_id=session_id, user_id=user_id, data=initial or {})
        self._contexts[session_id] = ctx
        return ctx

    def get(self, session_id: str) -> AgentContext:
        if session_id not in self._contexts:
            raise KeyError(f"unknown session {session_id}")
        return self._contexts[session_id]

    def update(self, session_id: str, data: Dict[str, Any]) -> AgentContext:
        ctx = self.get(session_id)
        ctx.data.update(data)
        return ctx

    def delete(self, session_id: str) -> None:
        self._contexts.pop(session_id, None)

    def persist_embedding(self, session_id: str, vector: list[float], metadata: Dict[str, Any]) -> None:
        payload = {
            "id": session_id,
            "vector": vector,
            "payload": metadata,
        }
        self._vector_client.upsert(collection="aionos-context", payload=payload)


__all__ = ["ContextManager", "AgentContext", "VectorStoreClient"]
