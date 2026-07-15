"""Compatibility export for the canonical in-process telemetry bus."""

from shared.telemetry.bus import TelemetryBus as EventBus

__all__ = ["EventBus"]
