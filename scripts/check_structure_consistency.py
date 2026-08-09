#!/usr/bin/env python3
"""Fail when the prospective working tree violates the canonical root layout."""

from __future__ import annotations

import shutil
import subprocess  # nosec B404 - invokes only the local Git executable below
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ALLOWED_DIRECTORIES = {
    "console",
    "gateway",
    "control",
    "runtime-daemon",
    "data",
    "registry",
    "policies",
    "schemas",
    "shared",
    "integrations",
    "packages",
    "deploy",
    "scripts",
    "tests",
    "docs",
}
REQUIRED_DIRECTORIES = {
    "console",
    "gateway",
    "control",
    "runtime-daemon",
    "data",
    "registry",
    "policies",
    "schemas",
    "shared",
    "integrations",
    "deploy",
    "tests",
}
FORBIDDEN_ROOTS = {
    "agents",
    "control-plane",
    "core",
    "database",
    "db",
    "docker",
    "eventbus",
    "execution",
    "infra",
    "models",
    "observability",
    "orchestration",
    "protos",
    "rust-runtime",
    "ui",
}


def _git_paths(*args: str) -> set[str]:
    git = shutil.which("git")
    if not git:
        raise RuntimeError("git executable is required for structure validation")
    result = subprocess.run(
        [git, "ls-files", *args],  # nosec B603 - fixed git subcommand and arguments
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return {line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip()}


def prospective_paths() -> set[str]:
    tracked = _git_paths()
    deleted = _git_paths("--deleted")
    untracked = _git_paths("--others", "--exclude-standard")
    return (tracked - deleted) | untracked


def main() -> int:
    paths = prospective_paths()
    directory_roots = {
        path.split("/", 1)[0]
        for path in paths
        if "/" in path and not path.startswith(".")
    }
    unexpected = sorted(directory_roots - ALLOWED_DIRECTORIES)
    missing = sorted(REQUIRED_DIRECTORIES - directory_roots)
    forbidden = sorted(directory_roots & FORBIDDEN_ROOTS)

    failures: list[str] = []
    if unexpected:
        failures.append(f"unexpected top-level directories: {unexpected}")
    if missing:
        failures.append(f"missing canonical directories: {missing}")
    if forbidden:
        failures.append(f"forbidden legacy roots: {forbidden}")

    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("Structure audit passed: prospective working tree uses canonical roots only.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
