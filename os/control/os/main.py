"""Service entrypoint that runs both HTTP and gRPC servers for the control plane."""
from __future__ import annotations

import asyncio
import logging
import signal
from contextlib import suppress

import uvicorn
from grpc_health.v1 import health_pb2

from os.control.os.config import get_settings
from os.control.os.grpc_server import create_grpc_server, set_health_status
from os.control.os.http import app as http_app

logger = logging.getLogger(__name__)

async def _serve_http(shutdown: asyncio.Event) -> None:
    settings = get_settings()
    host = settings.http_host
    port = settings.http_port
    config = uvicorn.Config(
        http_app,
        host=host,
        port=port,
        loop="asyncio",
        reload=False,
        lifespan="on",
        log_config=None,
    )
    server = uvicorn.Server(config)

    async def _run() -> None:
        await server.serve()
        shutdown.set()

    serve_task = asyncio.create_task(_run())
    try:
        await shutdown.wait()
    finally:
        if not server.should_exit:
            server.should_exit = True
        await serve_task


async def _serve_grpc(shutdown: asyncio.Event) -> None:
    settings = get_settings()
    server = create_grpc_server()
    await server.start()
    health_servicer = getattr(server, "_health_servicer", None)
    if health_servicer is not None:
        set_health_status(health_servicer, "", health_pb2.HealthCheckResponse.SERVING)
    logger.info("gRPC server listening on %s:%s", settings.grpc_host, settings.grpc_port)

    async def _wait_for_stop() -> None:
        await server.wait_for_termination()
        shutdown.set()

    waiter = asyncio.create_task(_wait_for_stop())
    try:
        await shutdown.wait()
    finally:
        if health_servicer is not None:
            set_health_status(health_servicer, "", health_pb2.HealthCheckResponse.NOT_SERVING)
        await server.stop(grace=5)
        await waiter


def _install_signal_handlers(shutdown: asyncio.Event) -> None:
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        with suppress(NotImplementedError):  # pragma: no cover - platform specific
            loop.add_signal_handler(sig, shutdown.set)


async def _main_async() -> None:
    logging.basicConfig(level=logging.INFO)
    shutdown = asyncio.Event()
    _install_signal_handlers(shutdown)

    await asyncio.gather(_serve_http(shutdown), _serve_grpc(shutdown))


def main() -> None:
    """Entry point used by ``python -m os.control.os.main``."""
    asyncio.run(_main_async())


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    main()
