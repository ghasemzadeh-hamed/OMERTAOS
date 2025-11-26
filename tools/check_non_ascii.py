#!/usr/bin/env python3
"""
Scan tracked repository files for non-ASCII characters.
Exits with status 1 if any offending lines are found.
"""
from __future__ import annotations
import subprocess
import sys
from pathlib import Path

def is_binary(data: bytes) -> bool:
    return b"\0" in data

def iter_tracked_files() -> list[Path]:
    root = Path(__file__).resolve().parent.parent
    output = subprocess.check_output(["git", "ls-files"], cwd=root)
    return [root / Path(line.strip().decode("utf-8")) for line in output.splitlines()]

def find_non_ascii_lines(path: Path) -> list[int]:
    data = path.read_bytes()
    if is_binary(data):
        return []
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return []
    lines: list[int] = []
    for idx, line in enumerate(text.splitlines(), 1):
        if any(ord(ch) > 127 for ch in line):
            lines.append(idx)
    return lines

def main() -> int:
    offenders: list[tuple[Path, list[int]]] = []
    for path in iter_tracked_files():
        non_ascii_lines = find_non_ascii_lines(path)
        if non_ascii_lines:
            offenders.append((path, non_ascii_lines))
    if offenders:
        for path, lines in offenders:
            joined = ", ".join(str(line) for line in lines)
            print(f"{path}: {joined}")
        return 1
    print("All tracked files are ASCII-only.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
