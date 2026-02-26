#!/usr/bin/env python3
from __future__ import annotations

import ast
import hashlib
import json
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCAN_DIRS = [
    "agents",
    "control-plane",
    "domain",
    "execution",
    "gateway",
    "registry",
    "database",
    "rust-runtime",
    "schemas",
    "services",
    "core",
]
TEMP_HINTS = ("tmp", "temp", "old", "draft", "backup", ".bak", ".orig", ".rej")
CONFIG_FILES = {".env", "settings.yaml", "settings.yml", "config.yaml", "config.yml", "pyproject.toml", "package.json", "Cargo.toml"}


def _files() -> list[Path]:
    files: list[Path] = []
    for base in SCAN_DIRS:
        root = REPO_ROOT / base
        if not root.exists():
            continue
        files.extend([p for p in root.rglob("*") if p.is_file()])
    return files


def find_duplicate_files(files: list[Path]) -> dict[str, list[str]]:
    by_hash: dict[str, list[str]] = defaultdict(list)
    for path in files:
        if path.stat().st_size > 1_000_000:
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        by_hash[digest].append(str(path.relative_to(REPO_ROOT)))
    return {k: v for k, v in by_hash.items() if len(v) > 1}


def find_temp_files(files: list[Path]) -> list[str]:
    hits: list[str] = []
    for p in files:
        lower = p.name.lower()
        if any(token in lower for token in TEMP_HINTS):
            hits.append(str(p.relative_to(REPO_ROOT)))
    return sorted(hits)


def find_large_files(files: list[Path], threshold_mb: int = 10) -> list[dict[str, str]]:
    large: list[dict[str, str]] = []
    for p in files:
        size = p.stat().st_size
        if size >= threshold_mb * 1024 * 1024:
            large.append({"file": str(p.relative_to(REPO_ROOT)), "size_mb": f"{size / 1024 / 1024:.2f}"})
    return sorted(large, key=lambda x: float(x["size_mb"]), reverse=True)


def find_python_unused_imports() -> dict[str, list[str]]:
    violations: dict[str, list[str]] = {}
    for p in REPO_ROOT.rglob("*.py"):
        if any(part.startswith(".") for part in p.parts) or "node_modules" in p.parts:
            continue
        try:
            tree = ast.parse(p.read_text(encoding="utf-8"), filename=str(p))
        except SyntaxError:
            continue
        imported: dict[str, str] = {}
        used: set[str] = set()
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                for a in n.names:
                    imported[a.asname or a.name.split(".")[0]] = a.name
            elif isinstance(n, ast.ImportFrom):
                for a in n.names:
                    if a.name != "*":
                        imported[a.asname or a.name] = f"{n.module}.{a.name}" if n.module else a.name
            elif isinstance(n, ast.Name):
                used.add(n.id)
        unused = sorted({v for k, v in imported.items() if k not in used})
        if unused:
            violations[str(p.relative_to(REPO_ROOT))] = unused
    return violations


def find_config_sources() -> list[str]:
    found: list[str] = []
    for p in REPO_ROOT.rglob("*"):
        if not p.is_file():
            continue
        if p.name in CONFIG_FILES or p.suffix in {".env", ".ini"}:
            found.append(str(p.relative_to(REPO_ROOT)))
    return sorted(found)


def architecture_violations() -> list[str]:
    violations: list[str] = []
    layer_roots = ["gateway", "control-plane", "domain", "execution", "database"]
    forbidden = {
        "domain": ("gateway", "execution", "control-plane/services"),
        "gateway": ("database", "execution"),
        "execution": ("gateway",),
    }
    for layer in layer_roots:
        root = REPO_ROOT / layer
        if not root.exists():
            continue
        for p in root.rglob("*.py"):
            text = p.read_text(encoding="utf-8", errors="ignore")
            for target in forbidden.get(layer, ()):
                if f"import {target.replace('/', '.')}" in text or f"from {target.replace('/', '.')}" in text:
                    violations.append(f"{p.relative_to(REPO_ROOT)} imports forbidden {target}")
    return sorted(violations)


def main() -> None:
    files = _files()
    report = {
        "duplicate_files": find_duplicate_files(files),
        "temporary_or_backup_files": find_temp_files(files),
        "large_files": find_large_files(files),
        "unused_imports": find_python_unused_imports(),
        "config_sources": find_config_sources(),
        "architecture_violations": architecture_violations(),
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
