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
                    capabilities=[
                        "terminal.execute"
                    ],
                ),
                argv=list(envelope.argv),
            )

            response = await stub.ExecuteCommand(
                request,
                timeout=timeout_seconds,
            )

            return {
                "ok": response.ok,
                "stdout": response.stdout,
                "stderr": response.stderr,
                "code": response.code,
            }

        finally:
            await channel.close()
