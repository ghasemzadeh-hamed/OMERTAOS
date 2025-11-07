from __future__ import annotations

from datetime import timedelta
from pymongo.collection import Collection


def ensure_ttl(collection: Collection, days: int) -> None:
    ttl_seconds = int(timedelta(days=days).total_seconds())
    collection.create_index([("created_at", 1)], expireAfterSeconds=ttl_seconds, name="created_at_ttl", background=True)
