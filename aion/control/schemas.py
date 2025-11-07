from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel


class UpsertPayload(BaseModel):
    category: str
    tool: Dict[str, Any]


class InstallReq(BaseModel):
    env: str = "default"
    version: Optional[str] = None
    editable: bool = False
    repo_url: Optional[str] = None


class SaveConfigReq(BaseModel):
    env: str = "default"
    config: Dict[str, Any]
