"""Pydantic models for router policy management."""
from __future__ import annotations

from typing import Dict, List

from pydantic import BaseModel


class RouterPolicyDocument(BaseModel):
    version: str = "0.0.0"
    default: str
    rules: list
    budgets: Dict[str, object] | None = None


class RouterPolicyHistory(BaseModel):
    revision: int
    checksum: str
    version: str
    applied_at: float


class RouterPolicyResponse(BaseModel):
    revision: int
    document: RouterPolicyDocument
    checksum: str
    history: List[RouterPolicyHistory] | None = None
