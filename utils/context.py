"""Lightweight repository context loader for the dev kernel."""

from __future__ import annotations

from pathlib import Path
from typing import List

BASE_DIR = Path(__file__).resolve().parents[2]

INCLUDE_DEFAULT = [
    "app",
    "gateway",
    "control",
    "console",
    "docker-compose.yml",
    "docker-compose.yaml",
    "pyproject.toml",
]

EXCLUDE_DIRS = {".git", "node_modules", "dist", "__pycache__"}


def _should_skip(path: Path) -> bool:
    if any(part in EXCLUDE_DIRS for part in path.parts):
        return True
    return False


def load_relevant_context(query: str, max_chars: int = 32000) -> str:
    """Return a deterministic snapshot of repository files for coding context."""

    unused_query = query  # reserved for future retrieval logic
    _ = unused_query
    chunks: List[str] = []
    total = 0

    for include in INCLUDE_DEFAULT:
        candidate = BASE_DIR / include
        if candidate.is_file():
            try:
                snippet = candidate.read_text(encoding="utf-8")[:4000]
            except Exception:
                continue
            chunks.append(f"# FILE: {include}\n{snippet}")
        elif candidate.is_dir():
            for item in candidate.rglob("*"):
                if item.is_dir():
                    continue
                if _should_skip(item.relative_to(BASE_DIR)):
                    continue
                if item.suffix not in {".py", ".ts", ".tsx", ".json", ".toml", ".yaml", ".yml", ".sh", ".ps1", ".env"}:
                    continue
                try:
                    snippet = item.read_text(encoding="utf-8")
                except Exception:
                    continue
                snippet = snippet.strip()
                if not snippet:
                    continue
                chunks.append(f"# FILE: {item.relative_to(BASE_DIR)}\n{snippet[:2000]}")
                total += len(chunks[-1])
                if total >= max_chars:
                    return "\n\n".join(chunks)
        total = sum(len(chunk) for chunk in chunks)
        if total >= max_chars:
            break

    return "\n\n".join(chunks)


__all__ = ["load_relevant_context"]
