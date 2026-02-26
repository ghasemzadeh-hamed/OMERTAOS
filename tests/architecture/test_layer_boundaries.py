from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _python_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return [p for p in root.rglob("*.py") if "__pycache__" not in p.parts]


def _imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.append(node.module)
    return imported


def _assert_no_imports(files: list[Path], forbidden_prefixes: tuple[str, ...], reason: str) -> None:
    violations: list[str] = []
    for path in files:
        rel = path.relative_to(REPO_ROOT)
        for module in _imports(path):
            if module.startswith(forbidden_prefixes):
                violations.append(f"{rel}: {module}")
    assert not violations, f"{reason}\n" + "\n".join(sorted(violations))


def test_kernel_does_not_import_control_runtime() -> None:
    files = _python_files(REPO_ROOT / "kernel")
    _assert_no_imports(
        files,
        forbidden_prefixes=("control", "control.os"),
        reason="kernel must not import control runtime modules",
    )


def test_data_does_not_import_kernel() -> None:
    files = _python_files(REPO_ROOT / "data")
    _assert_no_imports(
        files,
        forbidden_prefixes=("kernel",),
        reason="data plane must not import kernel modules",
    )


def test_services_does_not_import_kernel() -> None:
    files = _python_files(REPO_ROOT / "services")
    _assert_no_imports(
        files,
        forbidden_prefixes=("kernel",),
        reason="services must not import kernel modules",
    )
