from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

LAYERS = [
    "console",
    "gateway",
    "control",
    "domain",
    "orchestration",
    "data",
    "observability",
    "policies",
]


def _py_files(root: Path) -> list[Path]:
    return [p for p in root.rglob("*.py") if "__pycache__" not in p.parts] if root.exists() else []


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    mods: set[str] = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            mods.update(a.name for a in n.names)
        elif isinstance(n, ast.ImportFrom) and n.module:
            mods.add(n.module)
    return mods


def test_no_runtime_logic_inside_python_layers() -> None:
    violations: list[str] = []
    checked = ["domain", "orchestration", "control", "gateway", "data"]
    for layer in checked:
        for p in _py_files(REPO_ROOT / layer):
            for mod in _imports(p):
                if any(
                    mod == forbidden or mod.startswith(f"{forbidden}.")
                    for forbidden in ("ctypes", "fcntl", "pwd", "grp")
                ):
                    violations.append(f"{p.relative_to(REPO_ROOT)} -> {mod}")
    assert not violations, "python layers include OS-level logic imports:\n" + "\n".join(sorted(violations))


def test_control_runtime_access_via_runtime_client_only() -> None:
    forbidden = ("subprocess", "os.system")
    violations: list[str] = []
    for p in _py_files(REPO_ROOT / "control"):
        if "runtime" in p.parts or "runtime_client" in p.name:
            continue
        source = p.read_text(encoding="utf-8")
        if any(x in source for x in forbidden):
            violations.append(str(p.relative_to(REPO_ROOT)))
    assert not violations, "control bypassed runtime client boundary: " + ", ".join(sorted(violations))
