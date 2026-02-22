"""Compatibility shim for relocated :mod:`shared.secret_store.provider`."""

from __future__ import annotations

from shared.secret_store.provider import SecretProvider, SecretProviderError, get_secret_provider

__all__ = ["SecretProvider", "SecretProviderError", "get_secret_provider"]
