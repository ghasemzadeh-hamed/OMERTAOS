"""Transport-neutral audit record primitives.

This module creates an in-memory record only. Persistence and export belong to
an integration adapter and are intentionally outside this primitive.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass(frozen=True, slots=True)
class AuditEntry:
    action: str
    actor: str
    tenant_id: str
    at: datetime


def emit_audit(action: str, actor: str, tenant_id: str) -> AuditEntry:
    return AuditEntry(action=action, actor=actor, tenant_id=tenant_id, at=datetime.now(UTC))
