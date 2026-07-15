"""Event-bus adapters for external and in-process transports."""

from integrations.eventbus.kafka import KafkaEventBus
from integrations.eventbus.local import LocalEventBus

__all__ = ["KafkaEventBus", "LocalEventBus"]
