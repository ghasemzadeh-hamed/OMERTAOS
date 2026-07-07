"""MongoDB retention helpers owned by the canonical data layer."""
from __future__ import annotations

from datetime import timedelta
from typing import Any, Protocol


class CollectionLike(Protocol):
    def create_index(self, keys: list[tuple[str, int]], **kwargs: Any) -> Any: ...


def ensure_ttl(collection: CollectionLike, days: int) -> None:
    if days <= 0:
        raise ValueError("retention days must be greater than zero")
    ttl_seconds = int(timedelta(days=days).total_seconds())
    collection.create_index(
        [("created_at", 1)],
        expireAfterSeconds=ttl_seconds,
        name="created_at_ttl",
        background=True,
    )


__all__ = ["CollectionLike", "ensure_ttl"]
