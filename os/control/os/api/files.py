"""Filesystem utilities exposed through the control plane."""
from __future__ import annotations

import csv
from datetime import datetime
import io
import json
import os
from pathlib import Path
import shutil
from typing import Any, Iterable

from fastapi import APIRouter, Depends, HTTPException, Query, status

from .security import admin_or_devops_required


router = APIRouter(prefix="/api/files", tags=["files"])


def _allowed_roots() -> list[Path]:
    raw = os.getenv("AION_ALLOWED_PATHS", "/models:/data:/logs:/config")
    roots = []
    for chunk in raw.split(":"):
        chunk = chunk.strip()
        if not chunk:
            continue
        root = Path(chunk).expanduser().resolve()
        if root.exists():
            roots.append(root)
    if not roots:
        roots.append(Path.cwd().resolve())
    return roots


def _mask_path(path: Path) -> str:
    return str(path)


def _within_allowed(path: Path) -> bool:
    resolved = path.resolve(strict=False)
    for root in _allowed_roots():
        try:
            resolved.relative_to(root)
            return True
        except ValueError:
            continue
    return False


def _resolve_path(path: str | None) -> Path:
    if not path or path.strip() in {"", "/"}:
        # Special placeholder representing the virtual root containing allowed
        # directories.  Handled by callers.
        raise ValueError("root")
    candidate = Path(path).expanduser()
    if not candidate.is_absolute():
        for root in _allowed_roots():
            joined = (root / candidate).resolve(strict=False)
            if _within_allowed(joined):
                return joined
    resolved = candidate.resolve(strict=False)
    if not _within_allowed(resolved):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="path not allowed")
    return resolved


def _list_virtual_roots() -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for root in _allowed_roots():
        stat = root.stat() if root.exists() else None
        entries.append(
            {
                "name": root.name or str(root),
                "path": str(root),
                "type": "directory",
                "size": stat.st_size if stat else 0,
                "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat() if stat else None,
            }
        )
    return entries


def _list_directory(target: Path) -> list[dict[str, Any]]:
    if not target.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="path not found")
    if not target.is_dir():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="not a directory")
    entries: list[dict[str, Any]] = []
    for item in sorted(target.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())):
        stat = item.stat()
        entries.append(
            {
                "name": item.name,
                "path": str(item.resolve()),
                "type": "directory" if item.is_dir() else "file",
                "size": stat.st_size,
                "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            }
        )
    return entries


@router.get("/list")
async def list_files(
    path: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(200, ge=1, le=500),
) -> dict[str, Any]:
    try:
        target = _resolve_path(path)
    except ValueError:
        entries = _list_virtual_roots()
        return {"path": None, "entries": entries, "page": 1, "total": len(entries)}
    entries = _list_directory(target)
    total = len(entries)
    start = (page - 1) * page_size
    end = start + page_size
    return {
        "path": str(target.resolve()),
        "entries": entries[start:end],
        "page": page,
        "total": total,
    }


@router.post("/mkdir")
async def mkdir(payload: dict[str, str], principal=Depends(admin_or_devops_required())) -> dict[str, Any]:
    path = payload.get("path")
    if not path:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="path required")
    target = _resolve_path(path)
    target.mkdir(parents=True, exist_ok=True)
    return {"ok": True, "path": str(target)}


def _ensure_mutable(path: Path) -> None:
    if not _within_allowed(path):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="path not allowed")


@router.post("/delete")
async def delete(payload: dict[str, str], principal=Depends(admin_or_devops_required())) -> dict[str, Any]:
    path = payload.get("path")
    if not path:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="path required")
    target = _resolve_path(path)
    _ensure_mutable(target)
    if target.is_dir():
        shutil.rmtree(target)
    elif target.exists():
        target.unlink()
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="path not found")
    return {"ok": True}


@router.post("/rename")
async def rename(payload: dict[str, str], principal=Depends(admin_or_devops_required())) -> dict[str, Any]:
    path = payload.get("path")
    new_name = payload.get("new_name")
    if not path or not new_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="path and new_name required")
    target = _resolve_path(path)
    _ensure_mutable(target)
    if "/" in new_name or new_name.strip() == "":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid name")
    destination = target.with_name(new_name)
    target.rename(destination)
    return {"ok": True, "path": str(destination)}


@router.get("/content")
async def get_content(path: str) -> dict[str, Any]:
    target = _resolve_path(path)
    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="file not found")
    try:
        text = target.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="binary file")
    return {"path": str(target), "content": text}


@router.post("/save")
async def save_content(
    payload: dict[str, str],
    principal=Depends(admin_or_devops_required()),
) -> dict[str, Any]:
    path = payload.get("path")
    content = payload.get("content")
    if not path:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="path required")
    if content is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="content required")
    target = _resolve_path(path)
    if target.exists() and not target.is_file():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="not a file")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return {"ok": True, "path": str(target)}


@router.get("/preview", deprecated=True)
async def deprecated_preview() -> dict[str, str]:
    """Backward compatible placeholder for the old preview endpoint."""
    raise HTTPException(status_code=status.HTTP_410_GONE, detail="use /api/data/preview")


def _preview_csv(path: Path, limit: int) -> dict[str, Any]:
    rows: list[list[str]] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        headers: list[str] | None = None
        for idx, row in enumerate(reader):
            if idx == 0:
                headers = row
                continue
            rows.append(row)
            if len(rows) >= limit:
                break
    return {
        "type": "csv",
        "columns": headers or [],
        "rows": rows,
    }


def _preview_json(path: Path, limit: int) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    if isinstance(data, list):
        rows = data[:limit]
    else:
        rows = data
    return {
        "type": "json",
        "content": rows,
        "top_level_keys": list(rows.keys()) if isinstance(rows, dict) else [],
    }


def preview_data(path: Path, limit: int) -> dict[str, Any]:
    suffix = path.suffix.lower()
    if suffix in {".csv", ".tsv"}:
        return _preview_csv(path, limit)
    if suffix in {".json", ".jsonl"}:
        return _preview_json(path, limit)
    return {"unsupported_type": True}


@router.get("/../data/preview")
async def guard_preview_alias() -> dict[str, Any]:  # pragma: no cover - defensive
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


data_router = APIRouter(prefix="/api/data", tags=["data"])


@data_router.get("/preview")
async def data_preview(path: str, limit: int = Query(100, ge=1, le=1000)) -> dict[str, Any]:
    target = _resolve_path(path)
    if not target.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="file not found")
    if target.is_dir():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="not a file")
    try:
        result = preview_data(target, limit)
    except UnicodeDecodeError:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="binary file")
    return {"path": str(target), **result}


__all__ = ["router", "data_router"]
