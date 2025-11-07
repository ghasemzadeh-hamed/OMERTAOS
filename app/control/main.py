"""Compatibility layer for historical imports of the control FastAPI app."""
from app.control.app.http import app, health, healthz  # re-export

__all__ = ["app", "health", "healthz"]
