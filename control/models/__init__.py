"""Compatibility shim for ``os.control.models``."""

from __future__ import annotations

from .registry import ModelRegistry, PrivacyLevel, get_model_registry

__all__ = ["ModelRegistry", "PrivacyLevel", "get_model_registry"]
