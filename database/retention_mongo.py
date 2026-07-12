"""Legacy exports; new code imports from data.retention_mongo."""

from data.retention_mongo import CollectionLike, ensure_ttl

__all__ = ["CollectionLike", "ensure_ttl"]
