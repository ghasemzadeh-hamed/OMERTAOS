from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _py_files(path: Path) -> list[Path]:
    return [p for p in path.rglob("*.py") if "__pycache__" not in p.parts] if path.exists() else []


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    mods: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            mods.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            mods.add(node.module)
    return mods


def test_domain_has_no_service_or_gateway_imports() -> None:
    violations: list[str] = []
    for p in _py_files(REPO_ROOT / "domain"):
        for mod in _imports(p):
            if mod.startswith(("control_plane.services", "gateway", "control-plane.services")):
                violations.append(f"{p.relative_to(REPO_ROOT)} -> {mod}")
    assert not violations, "domain imported forbidden transport modules:\n" + "\n".join(sorted(violations))


def test_gateway_has_no_database_imports() -> None:
    violations: list[str] = []
    for p in _py_files(REPO_ROOT / "gateway"):
        for mod in _imports(p):
            if mod.startswith(("database", "sqlalchemy", "psycopg2", "motor", "redis")):
                violations.append(f"{p.relative_to(REPO_ROOT)} -> {mod}")
    assert not violations, "gateway imported database modules:\n" + "\n".join(sorted(violations))
