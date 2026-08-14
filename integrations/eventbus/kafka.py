"""Kafka EventBus adapter boundary.

Transport wiring remains intentionally unavailable until its delivery,
serialization and consumer-group semantics are specified and tested.
"""

from __future__ import annotations

from control.ports.event_bus import DomainEvent, EventBus, EventHandler


class KafkaEventBus(EventBus):
    def __init__(self, bootstrap_servers: str, topic_prefix: str = "omertaos") -> None:
        self.bootstrap_servers = bootstrap_servers
        self.topic_prefix = topic_prefix

    async def publish(self, event: DomainEvent) -> None:
        raise NotImplementedError("wire aiokafka producer here and publish serialized DomainEvent")

    async def subscribe(self, event_name: str, handler: EventHandler) -> None:
        raise NotImplementedError("wire aiokafka consumer group and dispatch to handler")
