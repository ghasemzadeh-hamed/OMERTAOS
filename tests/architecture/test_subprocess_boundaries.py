from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _py_files() -> list[Path]:
    roots = [REPO_ROOT / "control", REPO_ROOT / "domain", REPO_ROOT / "orchestration", REPO_ROOT / "data"]
    out: list[Path] = []
    for r in roots:
        if r.exists():
            out.extend([p for p in r.rglob("*.py") if "__pycache__" not in p.parts])
    return out


def test_subprocess_only_allowed_in_runtime_client() -> None:
    violations: list[str] = []
    for p in _py_files():
        tree = ast.parse(p.read_text(encoding="utf-8"), filename=str(p))
        has_subprocess = False
        for n in ast.walk(tree):
            if isinstance(n, ast.Import) and any(a.name == "subprocess" for a in n.names):
                has_subprocess = True
            if isinstance(n, ast.ImportFrom) and n.module == "subprocess":
                has_subprocess = True
        if has_subprocess and "runtime" not in p.parts and "runtime_client" not in p.name:
            violations.append(str(p.relative_to(REPO_ROOT)))
    assert not violations, "subprocess usage found outside runtime_client: " + ", ".join(sorted(violations))
