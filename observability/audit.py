from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, UTC


@dataclass(frozen=True, slots=True)
class AuditEntry:
    action: str
    actor: str
    tenant_id: str
    at: datetime


def emit_audit(action: str, actor: str, tenant_id: str) -> AuditEntry:
    return AuditEntry(action=action, actor=actor, tenant_id=tenant_id, at=datetime.now(UTC))
