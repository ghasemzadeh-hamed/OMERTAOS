from __future__ import annotations

from typing import Optional
from __future__ import annotations

from typing import Optional

from qdrant_client import QdrantClient
from qdrant_client.http import models as rest_models
from pydantic_settings import BaseSettings


class QdrantSettings(BaseSettings):
    url: str = "http://qdrant:6333"
    api_key: Optional[str] = None

    class Config:
        env_prefix = "QDRANT_"
        env_file = ".env"


def collection_name(base: str, tenant_id: Optional[str]) -> str:
    return f"{tenant_id or 'default'}__{base}"


def create_qdrant_client() -> QdrantClient:
    settings = QdrantSettings()
    return QdrantClient(url=settings.url, api_key=settings.api_key)


def ensure_collection(client: QdrantClient, base_name: str, tenant_id: Optional[str] = None) -> str:
    name = collection_name(base_name, tenant_id)
    existing = client.get_collections().collections
    if not any(col.name == name for col in existing):
        client.recreate_collection(
            collection_name=name,
            vectors_config=rest_models.VectorParams(size=1536, distance=rest_models.Distance.COSINE),
        )
    return name
