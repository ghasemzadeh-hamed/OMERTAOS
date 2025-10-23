from __future__ import annotations

import json
from typing import Any

import grpc

from ..config import get_settings
from ..services.protobuf import execution_pb2, execution_pb2_grpc

settings = get_settings()


async def execute_local_module(task_id: str, intent: str, params: dict[str, Any]) -> dict[str, Any]:
    endpoint = settings.grpc_endpoint.replace('http://', '').replace('https://', '')
    async with grpc.aio.insecure_channel(endpoint) as channel:
        stub = execution_pb2_grpc.TaskModuleStub(channel)
        request = execution_pb2.TaskRequest(
            task_id=task_id,
            intent=intent,
            payload_json=json.dumps(params),
        )
        response = await stub.Execute(request)
        return {
            'result': json.loads(response.result_json or '{}'),
            'status': response.status,
        }
