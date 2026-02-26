from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PolicyUpdated:
    policy_id: str
    version: str
