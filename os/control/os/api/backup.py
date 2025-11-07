"""Backup orchestration endpoints."""
from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
import tarfile
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from .security import admin_required, admin_or_devops_required


router = APIRouter(prefix="/api/backup", tags=["backup"])

BACKUP_DIR = Path(os.getenv("AION_BACKUP_DIR", "backups"))
BACKUP_HISTORY = Path(os.getenv("AION_BACKUP_HISTORY", "backups/history.json"))
BACKUP_TARGET = os.getenv("AION_BACKUP_TARGET", str(BACKUP_DIR))


def _load_history() -> list[dict[str, Any]]:
    if not BACKUP_HISTORY.exists():
        return []
    return json.loads(BACKUP_HISTORY.read_text(encoding="utf-8"))


def _write_history(entries: list[dict[str, Any]]) -> None:
    BACKUP_HISTORY.parent.mkdir(parents=True, exist_ok=True)
    BACKUP_HISTORY.write_text(json.dumps(entries, indent=2, sort_keys=True), encoding="utf-8")


@router.get("/history")
async def history(principal=Depends(admin_or_devops_required())) -> dict[str, Any]:
    return {"history": _load_history()}


def _create_archive(target_dir: Path) -> Path:
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    archive_path = target_dir / f"aion-backup-{timestamp}.tar.gz"
    source_dirs = [
        Path("config"),
        Path("policies"),
        Path("models"),
    ]
    with tarfile.open(archive_path, "w:gz") as archive:
        for directory in source_dirs:
            if directory.exists():
                archive.add(directory, arcname=directory.name)
    return archive_path


@router.post("/run")
async def run_backup(principal=Depends(admin_required())) -> dict[str, Any]:
    target = Path(BACKUP_TARGET).expanduser()
    target.mkdir(parents=True, exist_ok=True)
    archive_path = _create_archive(target)
    entry = {
        "created_at": datetime.utcnow().isoformat() + "Z",
        "path": str(archive_path),
    }
    history_entries = _load_history()
    history_entries.append(entry)
    _write_history(history_entries[-50:])
    return {"ok": True, "archive": entry}


__all__ = ["router"]
