#!/usr/bin/env python3
"""Sanity check to ensure repository files only contain ASCII characters."""
from __future__ import annotations

import argparse
import pathlib
import sys
from typing import Iterable, List, Sequence, Set

DEFAULT_EXCLUDED_DIRS: Set[str] = {
    ".git",
    "node_modules",
    "target",
    "dist",
    "build",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".venv",
    "venv",
    "env",
    ".env",
    "coverage",
    ".tox",
    "tmp",
    "logs",
}
BYPASS_FILES: Set[pathlib.Path] = {
    pathlib.Path("CODE_OF_CONDUCT.md"),
    pathlib.Path("CONTRIBUTING.md"),
    pathlib.Path("README.md"),
    pathlib.Path("SECURITY.md"),
    pathlib.Path("ai_registry/README.md"),
    pathlib.Path("deploy/headless-bundle/README.md"),
    pathlib.Path("docs/agentos_ai_registry.md"),
    pathlib.Path("docs/deploy/headless-cli.md"),
    pathlib.Path("docs/deploy/terminal-explorer.md"),
    pathlib.Path("docs/events.md"),
    pathlib.Path("docs/logo.md"),
    pathlib.Path("docs/modules.md"),
}

BINARY_EXTENSIONS: Set[str] = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".ico",
    ".pdf",
    ".woff",
    ".woff2",
    ".ttf",
    ".otf",
    ".gz",
    ".zip",
    ".tar",
    ".tgz",
    ".mp4",
    ".webm",
    ".wasm",
}


def should_skip(path: pathlib.Path, root: pathlib.Path, include_hidden: bool) -> bool:
    parts = path.relative_to(root).parts
    if any(part in DEFAULT_EXCLUDED_DIRS for part in parts):
        return True
    if not include_hidden and any(part.startswith(".") for part in parts if part not in (".", "..")):
        return True
    return False


def iter_files(root: pathlib.Path, include_hidden: bool = False) -> Iterable[pathlib.Path]:
    for path in root.rglob("*"):
        if should_skip(path, root, include_hidden):
            continue
        if path.is_file():
            yield path


def is_binary(path: pathlib.Path) -> bool:
    if path.suffix.lower() in BINARY_EXTENSIONS:
        return True
    try:
        with path.open("rb") as fh:
            sample = fh.read(1024)
        return b"\0" in sample
    except OSError:
        return True


def check_ascii(paths: Sequence[pathlib.Path]) -> List[str]:
    failures: List[str] = []
    for path in paths:
        if not path.is_file():
            continue
        if path in BYPASS_FILES:
            continue
        if is_binary(path):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            failures.append(str(path))
            continue
        for idx, ch in enumerate(text, start=1):
            if ord(ch) > 127:
                failures.append(f"{path}:{idx}")
                break
    return failures


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify files are ASCII-only")
    parser.add_argument("paths", nargs="*", type=pathlib.Path, default=[pathlib.Path(".")])
    parser.add_argument("--include-hidden", action="store_true", help="Include hidden directories")
    args = parser.parse_args(argv)

    targets: List[pathlib.Path] = []
    for path in args.paths:
        if path.is_dir():
            targets.extend(iter_files(path, include_hidden=args.include_hidden))
        else:
            targets.append(path)

    failures = check_ascii(targets)
    if failures:
        joined = "\n".join(sorted(failures))
        sys.stderr.write("Non-ASCII characters detected in:\n" + joined + "\n")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
