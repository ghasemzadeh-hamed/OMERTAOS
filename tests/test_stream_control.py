import pytest

from app.control.app.aion_grpc.aion.v1 import tasks_pb2
from app.control.app.grpc_server import AionTasksService
from app.control.app.orchestrator import orchestrator
from app.control.app.router_engine import decision_engine


@pytest.mark.asyncio
async def test_route_decision_and_stream_ack():
    orchestrator._tasks.clear()  # type: ignore[attr-defined]

    payload = {
        "schema_version": "1.0",
        "task_id": "task-123",
        "intent": "invoice_ocr",
        "params": {"text": "hello world"},
        "preferred_engine": "auto",
        "priority": "normal",
        "sla": {"privacy": "local-only", "budget_usd": 0.01},
        "metadata": {"source": "test"},
        "tenant_id": "tenant-alpha",
    }

    task = orchestrator.create_task(payload)
    decision = decision_engine.decide(task)
    assert decision.route == "local"
    assert decision.reason in {"privacy_enforced", "policy_randomized"}

    await orchestrator.execute(task)
    service = AionTasksService()
    chunk = service._to_stream_chunk(task)
    assert chunk.control.requires_ack is True
    assert chunk.control.cursor.endswith("-final")
    assert chunk.control.retry.reason == "awaiting_ack"
    assert chunk.result.metadata["tenant_id"] == "tenant-alpha"

    acked = orchestrator.acknowledge_stream(task.task_id, chunk.control.cursor, "client-1")
    assert acked is True

    post_ack_chunk = service._to_stream_chunk(task)
    assert post_ack_chunk.control.retry.reason == ""
    assert orchestrator.acknowledge_stream(task.task_id, chunk.control.cursor, "client-1") is True


@pytest.mark.asyncio
async def test_stream_generator_respects_ack():
    orchestrator._tasks.clear()  # type: ignore[attr-defined]
    payload = {
        "schema_version": "1.0",
        "task_id": "task-999",
        "intent": "summarize",
        "params": {"text": "lorem ipsum"},
        "preferred_engine": "auto",
        "priority": "normal",
        "sla": {"budget_usd": 0.05},
        "metadata": {},
        "tenant_id": "tenant-beta",
    }
    task = orchestrator.create_task(payload)
    await orchestrator.execute(task)

    service = AionTasksService()

    class DummyContext:
        def __init__(self):
            self._code = None
            self._details = None

        def invocation_metadata(self):
            return (("tenant-id", "tenant-beta"),)

        def set_code(self, code):
            self._code = code

        def set_details(self, details):
            self._details = details

    context = DummyContext()
    request = tasks_pb2.TaskRequest(task_id=task.task_id)

    stream = service.Stream(request, context)  # type: ignore[arg-type]
    chunk = None
    async for message in stream:
        chunk = message
        break

    assert chunk is not None
    assert chunk.control.requires_ack
    assert chunk.control.cursor == task.stream_state.cursor
    assert context._code is None

    orchestrator.acknowledge_stream(task.task_id, chunk.control.cursor, "stream-client")
    post_ack_chunk = service._to_stream_chunk(task)
    assert post_ack_chunk.control.retry.reason == ""
