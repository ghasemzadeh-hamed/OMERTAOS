"""Log aggregation endpoints."""
from __future__ import annotations

from collections import deque
import os
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from .security import admin_or_devops_required


router = APIRouter(prefix="/api/logs", tags=["logs"])


def _log_streams() -> dict[str, Path]:
    mapping: dict[str, Path] = {}
    raw = os.getenv("AION_LOG_STREAMS")
    if raw:
        for chunk in raw.split(","):
            if not chunk.strip():
                continue
            name, _, path = chunk.partition(":")
            mapping[name.strip()] = Path(path.strip()).expanduser()
    else:
        base = Path(os.getenv("AION_LOG_DIR", "./logs"))
        mapping = {
            "gateway": base / "gateway.log",
            "control": base / "control.log",
            "console": base / "console.log",
            "kernel": base / "kernel.log",
            "agents": base / "agents.log",
        }
    return mapping


@router.get("/streams")
async def list_streams(principal=Depends(admin_or_devops_required())) -> dict[str, Any]:
    streams = _log_streams()
    return {"streams": [{"name": name, "path": str(path)} for name, path in streams.items()]}


def _tail(path: Path, lines: int, grep: str | None) -> list[str]:
    if not path.exists():
        return []
    buffer: deque[str] = deque(maxlen=lines)
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if grep and grep.lower() not in line.lower():
                continue
            buffer.append(line.rstrip())
    return list(buffer)


@router.get("/tail")
async def tail_stream(
    stream: str,
    lines: int = Query(200, ge=1, le=2000),
    grep: str | None = None,
    principal=Depends(admin_or_devops_required()),
) -> dict[str, Any]:
    streams = _log_streams()
    if stream not in streams:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="unknown stream")
    entries = _tail(streams[stream], lines, grep)
    return {"stream": stream, "entries": entries}


__all__ = ["router"]
