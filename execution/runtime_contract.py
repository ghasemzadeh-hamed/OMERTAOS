"""Compatibility exports for the canonical Control-to-Runtime contract."""

from control.clients.runtime import RuntimeEnvelope, RuntimeExecutor

RuntimeCommand = RuntimeEnvelope

__all__ = ["RuntimeCommand", "RuntimeExecutor"]
