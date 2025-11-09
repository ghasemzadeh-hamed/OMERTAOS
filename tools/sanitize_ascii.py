#!/usr/bin/env python3
"""
Fix non-ASCII characters in tracked text files so tools/sanitize_ascii.py passes.

- Respects:
  - DEFAULT_EXCLUDED_DIRS
  - BYPASS_FILES
  - BINARY_EXTENSIONS
- Applies a conservative mapping; unknown chars -> "?".
"""

from __future__ import annotations

import pathlib
from typing import Iterable, List, Sequence, Set

# Keep these in sync with sanitize_ascii.py
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
    pathlib.Path("console/app/(auth)/login/page.tsx"),
    pathlib.Path("console/app/(components)/VirtualKeyboard.tsx"),
    pathlib.Path("console/app/(dashboard)/layout.tsx"),
    pathlib.Path("console/app/(onboarding)/setup-index/page.tsx"),
    pathlib.Path("console/personal/ChatPanel.tsx"),
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

# Mapping of common non-ASCII characters to safe ASCII
REPLACE_MAP = {
    "\u2019": "'",
    "\u2018": "'",
    "\u201c": '"',
    "\u201d": '"',
    "\u2013": "-",
    "\u2014": "-",
    "\u2026": "...",
    "\u2022": "*",
    "\u00d7": "x",
    "\u00a9": "(c)",
    "\u00ae": "(r)",
    "\u2122": "(tm)",
    "\u00a0": " ",  # non-breaking space
    "\u202f": " ",  # narrow no-break space
}


def should_skip(path: pathlib.Path, root: pathlib.Path, include_hidden: bool) -> bool:
    parts = path.relative_to(root).parts
    if any(part in DEFAULT_EXCLUDED_DIRS for part in parts):
        return True
    if not include_hidden and any(
        part.startswith(".") for part in parts if part not in (".", "..")
    ):
        return True
    return False


def iter_files(root: pathlib.Path, include_hidden: bool = False) -> Iterable[pathlib.Path]:
    for path in root.rglob("*"):
        if path.is_file() and not should_skip(path, root, include_hidden):
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


MARKDOWN_EXTS = {".md", ".mdx"}
HTML_EXTS = {".html", ".htm"}
CODEPOINT_ESC_EXTS = {
    ".py",
    ".pyi",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".json",
    ".yaml",
    ".yml",
    ".sql",
    ".sh",
    ".ps1",
    ".toml",
    ".ini",
    ".cfg",
    ".conf",
}


def _format_replacement(codepoint: int, path: pathlib.Path) -> str:
    suffix = path.suffix.lower()
    if suffix in MARKDOWN_EXTS or suffix in HTML_EXTS:
        return f"&#x{codepoint:x};"
    if suffix in CODEPOINT_ESC_EXTS:
        if codepoint <= 0xFFFF:
            return f"\\u{codepoint:04x}"
        return f"\\U{codepoint:08x}"
    # Default to \u style for unknown extensions
    if codepoint <= 0xFFFF:
        return f"\\u{codepoint:04x}"
    return f"\\U{codepoint:08x}"


def sanitize_text(text: str, path: pathlib.Path) -> str:
    out_chars: List[str] = []
    changed = False

    for ch in text:
        if ord(ch) < 128:
            out_chars.append(ch)
            continue

        replacement = REPLACE_MAP.get(ch)
        if replacement is None:
            codepoint = ord(ch)
            if ch == "\ufeff":
                # Drop BOMs entirely
                changed = True
                continue
            replacement = _format_replacement(codepoint, path)
        out_chars.append(replacement)
        changed = True

    return "".join(out_chars), changed


def main() -> int:
    root = pathlib.Path(".").resolve()
    fixed_any = False

    for path in iter_files(root, include_hidden=False):
        rel = path.relative_to(root)

        if rel in BYPASS_FILES:
            continue
        if is_binary(path):
            continue

        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # If we cannot decode as UTF-8, leave it; sanitize_ascii will flag it.
            print(f"[SKIP-DECODE] {rel}")
            continue

        sanitized, changed = sanitize_text(text, rel)
        if changed:
            path.write_text(sanitized, encoding="utf-8")
            print(f"[FIXED] {rel}")
            fixed_any = True

    if not fixed_any:
        print("No changes needed. All non-bypass text files are ASCII-clean.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
