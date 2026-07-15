"""Compatibility export for the canonical telemetry exporter contract."""

from integrations.observability.exporter import TelemetryExporter as EventBus

__all__ = ["EventBus"]
