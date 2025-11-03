"""Helper entrypoint for running the Control API with uvicorn."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
import uvicorn

from app.main import app


def _load_env() -> None:
    """Load environment variables from a configured .env file."""
    explicit_env = os.environ.get("ENV_FILE")
    candidate_paths: list[Path] = []

    if explicit_env:
        candidate_paths.append(Path(explicit_env))

    working_dir_env = Path.cwd() / ".env"
    candidate_paths.append(working_dir_env)

    repo_root_env = Path(__file__).resolve().parent.parent / ".env"
    candidate_paths.append(repo_root_env)

    for env_path in candidate_paths:
        if env_path.exists():
            load_dotenv(env_path, override=False)


def main() -> None:
    _load_env()
    host = os.environ.get("CONTROL_HOST", os.environ.get("APP_HOST", "0.0.0.0"))
    port_value = (
        os.environ.get("CONTROL_PORT")
        or os.environ.get("AION_CONTROL_PORT")
        or os.environ.get("PORT")
        or "8000"
    )
    try:
        port = int(port_value)
    except ValueError:
        port = 8000

    workers_value = os.environ.get("CONTROL_WORKERS", "1")
    try:
        workers = int(workers_value)
    except ValueError:
        workers = 1

    uvicorn.run(app, host=host, port=port, workers=workers)


if __name__ == "__main__":
    main()
