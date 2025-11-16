import asyncio
import logging
from typing import Any, Callable

from google.protobuf.json_format import MessageToDict
import grpc
from grpc import aio
from grpc_health.v1 import health, health_pb2, health_pb2_grpc

from os.control.os.aion_grpc.aion.v1 import tasks_pb2, tasks_pb2_grpc
from os.control.os.config import get_settings
from os.control.os.models import TaskStatus
from os.control.os.orchestrator import orchestrator

logger = logging.getLogger(__name__)


class AionTasksService(tasks_pb2_grpc.AionTasksServicer):
    async def Submit(self, request: tasks_pb2.TaskRequest, context: aio.ServicerContext):
        payload = MessageToDict(request, preserving_proto_field_name=True)
        from uuid import uuid4

        payload.setdefault("schema_version", "1.0")
        task_id = request.task_id or payload.get("task_id") or f"task-{uuid4()}"
        tenant_id = payload.get("tenant_id") or self._extract_tenant(context)
        if tenant_id:
            payload["tenant_id"] = tenant_id
        task = orchestrator.create_task({**payload, "task_id": task_id})
        await orchestrator.execute(task)
        return self._to_proto(task)

    async def Stream(self, request: tasks_pb2.TaskRequest, context: aio.ServicerContext):
        task_id = request.task_id
        tenant_id = self._extract_tenant(context)
        attempt = 0
        while True:
            task = orchestrator.get_task(task_id)
            if not task:
                await asyncio.sleep(0.1)
                attempt += 1
                if attempt > 50:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details("task not found")
                    return
                continue
            if tenant_id and task.tenant_id and task.tenant_id != tenant_id:
                context.set_code(grpc.StatusCode.PERMISSION_DENIED)
                context.set_details("tenant mismatch")
                return
            if task.status in {TaskStatus.OK, TaskStatus.ERROR, TaskStatus.TIMEOUT, TaskStatus.CANCELED}:
                chunk = self._to_stream_chunk(task)
                yield chunk
                if chunk.control.final:
                    return
            attempt += 1
            await asyncio.sleep(0.1)

    async def StatusById(self, request: tasks_pb2.TaskId, context: aio.ServicerContext):
        task = orchestrator.get_task(request.task_id)
        if not task:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("task not found")
            return tasks_pb2.TaskResult()
        tenant_id = self._extract_tenant(context)
        if tenant_id and task.tenant_id and task.tenant_id != tenant_id:
            context.set_code(grpc.StatusCode.PERMISSION_DENIED)
            context.set_details("tenant mismatch")
            return tasks_pb2.TaskResult()
        return self._to_proto(task)

    async def AckStream(self, request: tasks_pb2.StreamAck, context: aio.ServicerContext):
        consumer_id = request.consumer_id or "default"
        task = orchestrator.get_task(request.task_id)
        if not task:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("task not found")
            return tasks_pb2.AckResponse(accepted=False)
        tenant_id = self._extract_tenant(context)
        if tenant_id and task.tenant_id and task.tenant_id != tenant_id:
            context.set_code(grpc.StatusCode.PERMISSION_DENIED)
            context.set_details("tenant mismatch")
            return tasks_pb2.AckResponse(accepted=False)
        accepted = orchestrator.acknowledge_stream(request.task_id, request.cursor, consumer_id)
        if not accepted:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("stream cursor not found")
            return tasks_pb2.AckResponse(accepted=False)
        return tasks_pb2.AckResponse(accepted=True, cursor=request.cursor)

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
        if task.tenant_id:
            result.metadata["tenant_id"] = task.tenant_id
        return result

    def _to_stream_chunk(self, task):
        proto_result = self._to_proto(task)
        ack_required = task.stream_state.requires_ack and not task.stream_state.acknowledged
        control = tasks_pb2.StreamControl(
            cursor=task.stream_state.cursor,
            final=True,
            requires_ack=ack_required,
            backpressure_hint=task.stream_state.backpressure_hint or "",
        )
        control.retry.reason = "awaiting_ack" if ack_required else ""
        control.retry.attempt = task.stream_state.retry_attempt
        control.retry.max_attempts = task.stream_state.max_attempts
        control.retry.retry_after_ms = task.stream_state.retry_after_ms
        return tasks_pb2.StreamChunk(result=proto_result, control=control)

    @staticmethod
    def _extract_tenant(context: aio.ServicerContext) -> str | None:
        for metadata in context.invocation_metadata():
            key, value = metadata
            if key.lower() in {"tenant-id", "x-tenant", "x-tenant-id"} and value:
                return value
        return None


def _set_health_status(health_servicer: Any, service: str, status: int) -> None:
    """Set gRPC health status across grpcio-health-checking API variants."""

    setter: Callable[[str, int], None] | None = getattr(health_servicer, "set", None)
    if setter is None:
        setter = getattr(health_servicer, "set_status", None)

    if callable(setter):
        setter(service, status)
    else:  # pragma: no cover - defensive guardrail for unexpected implementations
        logger.warning(
            "HealthServicer implementation %s lacks set/set_status; health status not updated",
            type(health_servicer).__name__,
        )


def set_health_status(health_servicer: Any, service: str, status: int) -> None:
    """Public compatibility wrapper for updating gRPC health status."""

    _set_health_status(health_servicer, service, status)


def create_grpc_server(host: str | None = None, port: int | None = None) -> aio.Server:
    settings = get_settings()
    resolved_host = host or settings.grpc_host
    resolved_port = port or settings.grpc_port
    server = aio.server()
    tasks_pb2_grpc.add_AionTasksServicer_to_server(AionTasksService(), server)

    health_servicer = health.HealthServicer()
    set_health_status(health_servicer, "", health_pb2.HealthCheckResponse.NOT_SERVING)
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)
    setattr(server, "_health_servicer", health_servicer)

    certificate_chain = settings.grpc_tls_certificate
    private_key = settings.grpc_tls_private_key
    if certificate_chain and private_key:
        root_certificates = settings.grpc_tls_client_ca
        credentials = grpc.ssl_server_credentials(
            [(private_key, certificate_chain)],
            root_certificates=root_certificates,
            require_client_auth=settings.grpc_require_client_cert,
        )
        server.add_secure_port(f"{resolved_host}:{resolved_port}", credentials)
    else:
        logger.warning(
            "TLS cert/key missing or Vault not initialised, falling back to insecure gRPC listener"
        )
        server.add_insecure_port(f"{resolved_host}:{resolved_port}")
    return server


async def serve() -> None:
    server = create_grpc_server()
    await server.start()
    health_servicer = getattr(server, "_health_servicer", None)
    if health_servicer is not None:
        set_health_status(health_servicer, "", health_pb2.HealthCheckResponse.SERVING)
    logger.info("gRPC server started")
    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())
