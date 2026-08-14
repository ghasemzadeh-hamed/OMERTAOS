"""Vault-backed secret provider utilities.

This package intentionally avoids the ``os.secrets`` name that previously clashed
with Python's standard-library :mod:`secrets` module. Renaming prevents import
resolution issues for third-party frameworks (for example Starlette) that rely
on ``from secrets import token_hex``.
"""
from __future__ import annotations

from .provider import SecretProvider, SecretProviderError, get_secret_provider

__all__ = ["SecretProvider", "SecretProviderError", "get_secret_provider"]
