from __future__ import annotations
from typing import TYPE_CHECKING

import grpc

from shared.generated.python.runtime import runtime_pb2
from shared.generated.python.runtime import runtime_pb2_grpc


if TYPE_CHECKING:
    from .client import RuntimeEnvelope


class GrpcRuntimeTransport:
    async def execute(
        self,
        endpoint: str,
        envelope: "RuntimeEnvelope",
        *,
        timeout_seconds: float,
    ) -> dict[str, object]:

        channel = grpc.aio.insecure_channel(endpoint)

        try:
            stub = runtime_pb2_grpc.RuntimeServiceStub(channel)

            request = runtime_pb2.CommandRequest(
                context=runtime_pb2.ExecutionContext(
                    agent_id=envelope.agent_id,
                    tenant_id=envelope.tenant_id,
                    capabilities=list(envelope.capabilities),
                ),
                argv=list(envelope.argv),
            )

            response = await stub.ExecuteCommand(
                request,
                timeout=timeout_seconds,
                metadata=_execution_metadata(envelope),
            )

            return {
                "ok": response.ok,
                "stdout": response.stdout,
                "stderr": response.stderr,
                "code": response.code,
            }

        finally:
            await channel.close()


def _execution_metadata(envelope: "RuntimeEnvelope") -> tuple[tuple[str, str], ...]:
    values = (
        ("tenant-id", envelope.tenant_id),
        ("x-aion-task-id", envelope.task_id),
        ("x-aion-attempt-id", envelope.attempt_id),
        ("x-request-id", envelope.request_id),
        ("traceparent", envelope.trace_id),
        ("x-aion-node-id", envelope.node_id),
        ("x-aion-lease-token", envelope.lease_token),
        (
            "x-aion-lease-generation",
            str(envelope.lease_generation) if envelope.lease_generation else "",
        ),
        (
            "x-aion-lease-expires-at-ms",
            str(envelope.lease_expires_at_ms) if envelope.lease_expires_at_ms else "",
        ),
    )
    return tuple((key, value) for key, value in values if value)
