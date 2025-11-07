"""Background workers that consume webhook events."""
from __future__ import annotations

import asyncio
from typing import Dict

from app.control.app.core.logger import get_logger
from app.control.app.core.state import ControlState, JobRecord

logger = get_logger(__name__)


ROUTING_TABLE = {
    "github.push": "ci-trigger",
    "odoo.invoice.paid": "accounting-sync",
}


async def worker_loop(state: ControlState, shutdown_event: asyncio.Event) -> None:
    """Continuously consume webhook events from the queue."""

    while not shutdown_event.is_set():
        try:
            event = await asyncio.wait_for(state.event_queue.get(), timeout=0.5)
        except asyncio.TimeoutError:
            continue
        _process_event(state, event)
        state.event_queue.task_done()


def _process_event(state: ControlState, event: Dict) -> None:
    event_type = event.get("event_type", "unknown")
    module = ROUTING_TABLE.get(f"{event.get('source')}.{event_type}")
    if module is None and event_type != "unknown":
        module = ROUTING_TABLE.get(event_type)
    if module is None:
        module = "dead-letter"
    status = "queued" if module != "dead-letter" else "ignored"
    detail = f"routed to {module}"
    record = JobRecord(
        event_id=event["event_id"],
        event_type=event_type,
        status=status,
        detail=detail,
    )
    state.record_job(record)
    logger.info("event processed", extra={"event_id": event["event_id"], "module_name": module})
