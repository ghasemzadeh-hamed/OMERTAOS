"""Pydantic models for router policy management."""
from __future__ import annotations

from typing import Dict

from pydantic import BaseModel


class RouterPolicyDocument(BaseModel):
    default: str
    rules: list
    budgets: Dict[str, object] | None = None


class RouterPolicyResponse(BaseModel):
    revision: int
    document: RouterPolicyDocument
