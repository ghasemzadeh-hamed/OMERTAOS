from __future__ import annotations

import os

import uvicorn

from control.transports.tasks_grpc import serve as serve_grpc


def main() -> None:
    grpc_server = serve_grpc()
    try:
        uvicorn.run(
            "control.app.main:app",
            host=os.getenv("AION_CONTROL_HTTP_HOST", "0.0.0.0"),
            port=int(os.getenv("AION_CONTROL_HTTP_PORT", "8000")),
        )
    finally:
        grpc_server.stop(grace=5)


if __name__ == "__main__":
    main()
