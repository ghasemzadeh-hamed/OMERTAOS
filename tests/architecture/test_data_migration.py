from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_legacy_data_roots_contain_no_class_or_function_implementations() -> None:
    allowed_function = {"database/__init__.py": {"__getattr__"}}
    violations: list[str] = []

    for root_name in ("database", "db"):
        for path in (REPO_ROOT / root_name).rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            relative = path.relative_to(REPO_ROOT).as_posix()
            allowed = allowed_function.get(relative, set())
            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    violations.append(f"{relative}: class {node.name}")
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name not in allowed:
                    violations.append(f"{relative}: function {node.name}")

    assert not violations, "legacy data implementation remains:\n" + "\n".join(sorted(violations))


def test_canonical_data_interfaces_exist() -> None:
    required = (
        "data/interfaces/__init__.py",
        "data/interfaces/adapter.py",
        "data/interfaces/repository.py",
    )
    assert all((REPO_ROOT / path).is_file() for path in required)
