"""Compatibility exports for canonical audit primitives."""

from shared.telemetry.audit import AuditEntry, emit_audit

__all__ = ["AuditEntry", "emit_audit"]
