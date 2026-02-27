from __future__ import annotations

from eventbus.interface import DomainEvent, EventBus, EventHandler


class KafkaEventBus(EventBus):
    def __init__(self, bootstrap_servers: str, topic_prefix: str = "omertaos") -> None:
        self.bootstrap_servers = bootstrap_servers
        self.topic_prefix = topic_prefix

    async def publish(self, event: DomainEvent) -> None:
        raise NotImplementedError("wire aiokafka producer here and publish serialized DomainEvent")

    async def subscribe(self, event_name: str, handler: EventHandler) -> None:
        raise NotImplementedError("wire aiokafka consumer group and dispatch to handler")
