"""Compatibility exports for the canonical Control EventBus port."""

from control.ports.event_bus import DomainEvent, EventBus, EventHandler

__all__ = ["DomainEvent", "EventBus", "EventHandler"]
