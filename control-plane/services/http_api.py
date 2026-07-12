"""Compatibility export; new code imports from control.app.health."""

from control.app.health import health, health_payload, router

__all__ = ["health", "health_payload", "router"]
