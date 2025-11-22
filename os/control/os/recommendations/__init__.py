"""Recommendation subsystem (e.g., latentbox-backed tool suggestions)."""

from .latentbox import FEATURE_LATENTBOX, load_latentbox_catalog, sync_latentbox_catalog
from .store import ToolResourceRecord, ToolResourceStore

__all__ = [
    "FEATURE_LATENTBOX",
    "ToolResourceRecord",
    "ToolResourceStore",
    "load_latentbox_catalog",
    "sync_latentbox_catalog",
]
