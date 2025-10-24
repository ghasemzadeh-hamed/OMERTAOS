import asyncio
import logging
from google.protobuf.json_format import MessageToDict
import grpc
from grpc import aio

from .grpc.aion.v1 import tasks_pb2, tasks_pb2_grpc
from .orchestrator import orchestrator

logger = logging.getLogger(__name__)


class AionTasksService(tasks_pb2_grpc.AionTasksServicer):
    async def Submit(self, request: tasks_pb2.TaskRequest, context: aio.ServicerContext):
        payload = MessageToDict(request, preserving_proto_field_name=True)
        from uuid import uuid4
        payload.setdefault("schema_version", "1.0")
        task_id = request.task_id or payload.get("task_id") or f"task-{uuid4()}"
        task = orchestrator.create_task({**payload, "task_id": task_id})
        await orchestrator.execute(task)
        return self._to_proto(task)

    async def Stream(self, request: tasks_pb2.TaskRequest, context: aio.ServicerContext):
        task_id = request.task_id
        for _ in range(5):
            task = orchestrator.get_task(task_id)
            if task:
                yield self._to_proto(task)
            await asyncio.sleep(1)

    async def StatusById(self, request: tasks_pb2.TaskId, context: aio.ServicerContext):
        task = orchestrator.get_task(request.task_id)
        if not task:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("task not found")
            return tasks_pb2.TaskResult()
        return self._to_proto(task)

    def _to_proto(self, task):
        result = tasks_pb2.TaskResult(
            schema_version=task.schema_version,
            task_id=task.task_id,
            intent=task.intent,
            status=task.status.value,
        )
        result.engine.route = task.engine_route or "unknown"
        result.engine.reason = task.engine_reason or "unknown"
        result.engine.chosen_by = task.engine_chosen_by or "policy"
        result.engine.tier = task.engine_tier or "tier0"
        for key, value in task.result.items():
            result.result[key] = str(value)
        if task.usage:
            result.usage.latency_ms = float(task.usage.get("latency_ms", 0.0))
            result.usage.tokens = int(task.usage.get("tokens", 0))
            result.usage.cost_usd = float(task.usage.get("cost_usd", 0.0))
        if task.error:
            result.error.code = str(task.error.get("code", ""))
            result.error.message = str(task.error.get("message", ""))
        return result


def create_grpc_server(host: str = "0.0.0.0", port: int = 50051) -> aio.Server:
    server = aio.server()
    tasks_pb2_grpc.add_AionTasksServicer_to_server(AionTasksService(), server)
    server.add_insecure_port(f"{host}:{port}")
    return server


async def serve() -> None:
    server = create_grpc_server()
    await server.start()
    logger.info("gRPC server started")
    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())
