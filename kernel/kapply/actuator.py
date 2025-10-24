"""Safe kernel actuator applying proposals with audit logs."""

from __future__ import annotations

from pathlib import Path
from typing import Dict
import json

from ..models import KernelChange, KernelProposal


class KernelActuator:
    """Applies kernel changes in a sandboxed, audit-friendly manner."""

    def __init__(self, audit_path: Path | None = None) -> None:
        self.audit_path = audit_path or Path("/tmp/aion_kernel_audit.jsonl")
        self.audit_path.parent.mkdir(parents=True, exist_ok=True)

    def apply(self, proposal: KernelProposal) -> Dict[str, object]:
        record = {
            "proposal": proposal.proposal_id,
            "changes": [self._apply_change(change) for change in proposal.changes],
        }
        self._write_audit({**record, "status": "APPLIED"})
        proposal.apply()
        return record

    def rollback(self, proposal: KernelProposal) -> Dict[str, object]:
        record = {
            "proposal": proposal.proposal_id,
            "changes": [
                {
                    "key": change.key,
                    "to": change.from_value,
                    "from": change.to_value,
                }
                for change in proposal.changes
            ],
        }
        self._write_audit({**record, "status": "ROLLED_BACK"})
        proposal.rollback()
        return record

    @staticmethod
    def _apply_change(change: KernelChange) -> Dict[str, object]:
        # In production this would interface with privileged helpers. Here we simply return change metadata.
        return {
            "key": change.key,
            "from": change.from_value,
            "to": change.to_value,
        }

    def _write_audit(self, payload: Dict[str, object]) -> None:
        with self.audit_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload) + "\n")
