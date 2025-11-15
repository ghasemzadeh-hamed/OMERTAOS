"""Composite health probe for the control service.

The Docker health check historically relied on an HTTP endpoint. In certain
boot sequences the HTTP server can take longer to become reachable even though
the gRPC control plane is already serving requests. This module first attempts
an HTTP probe and falls back to gRPC health before giving up, ensuring the
container becomes healthy as soon as one of the interfaces is ready.
"""
from __future__ import annotations

import asyncio
import os
import sys
from typing import Final

import grpc
import httpx
from grpc_health.v1 import health_pb2, health_pb2_grpc

_DEFAULT_HTTP_URL: Final[str] = "http://localhost:8000/healthz"
_DEFAULT_GRPC_TARGET: Final[str] = "localhost:50051"
_DEFAULT_TIMEOUT: Final[float] = 2.5


async def _check_http(url: str, timeout: float) -> bool:
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.get(url)
        response.raise_for_status()
    return True


async def _check_grpc(target: str, timeout: float) -> bool:
    options = [("grpc.enable_http_proxy", 0)]
    async with grpc.aio.insecure_channel(target, options=options) as channel:
        stub = health_pb2_grpc.HealthStub(channel)
        request = health_pb2.HealthCheckRequest(service="")
        response = await asyncio.wait_for(stub.Check(request), timeout=timeout)
    return response.status == health_pb2.HealthCheckResponse.SERVING


async def _probe() -> int:
    timeout = float(os.getenv("AION_CONTROL_HEALTH_TIMEOUT", _DEFAULT_TIMEOUT))
    http_url = os.getenv("AION_CONTROL_HEALTH_URL", _DEFAULT_HTTP_URL)
    grpc_target = os.getenv("AION_CONTROL_GRPC", _DEFAULT_GRPC_TARGET)

    try:
        if await _check_http(http_url, timeout):
            return 0
    except Exception:  # pragma: no cover - health checks should be resilient
        pass

    try:
        if await _check_grpc(grpc_target, timeout):
            return 0
    except Exception:  # pragma: no cover - propagate failure as unhealthy
        pass

    return 1


def main() -> None:
    exit_code = asyncio.run(_probe())
    sys.exit(exit_code)


if __name__ == "__main__":  # pragma: no cover
    main()
