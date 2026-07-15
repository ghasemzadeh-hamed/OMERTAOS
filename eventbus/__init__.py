
"""Legacy EventBus package retained as a compatibility surface until S5."""

from eventbus.interface import DomainEvent, EventBus, EventHandler
from eventbus.kafka_bus import KafkaEventBus
from eventbus.local_bus import LocalEventBus

__all__ = ["DomainEvent", "EventBus", "EventHandler", "KafkaEventBus", "LocalEventBus"]
