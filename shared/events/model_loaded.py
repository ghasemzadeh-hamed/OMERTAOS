from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelLoaded:
    model_id: str
    runtime: str
