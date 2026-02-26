"""Compatibility shim for ``data.rag.ingest``."""
from __future__ import annotations

from data.rag.ingest import *  # noqa: F403
from data.rag.ingest import __all__ as _all

__all__ = list(_all)
