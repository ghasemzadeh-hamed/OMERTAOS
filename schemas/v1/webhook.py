"""Versioned webhook envelope schemas."""
from __future__ import annotations

from datetime import datetime
from typing import Dict

from pydantic import BaseModel


class WebhookEnvelope(BaseModel):
    source: str
    event_type: str
    event_id: str
    occurred_at: datetime
    headers: Dict[str, str]
    payload: Dict | str
