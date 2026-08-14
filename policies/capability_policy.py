from __future__ import annotations


def is_capability_allowed(granted: set[str], required: str) -> bool:
    if required in granted:
        return True
    prefix = required.split(":", 1)[0]
    return any(cap == f"{prefix}:*" for cap in granted)
