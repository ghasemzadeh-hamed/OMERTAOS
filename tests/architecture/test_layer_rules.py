from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LAYERS = ("interface", "control", "services", "data", "kernel", "shared")


LEGACY_ALLOWED_IMPORTS = {
    ("control/os/routes/kernel_proposals.py", "kernel.runtime"),
    ("control/tests/test_kernel_proposals.py", "kernel.runtime"),
}


def _layer_for(path: Path) -> str | None:
    rel = path.relative_to(REPO_ROOT)
    return rel.parts[0] if rel.parts and rel.parts[0] in LAYERS else None


def _py_files(layer: str) -> list[Path]:
    root = REPO_ROOT / layer
    if not root.exists():
        return []
    return [p for p in root.rglob("*.py") if "__pycache__" not in p.parts]


def _imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.append(node.module)
    return modules


def test_forbidden_imports() -> None:
    violations: list[str] = []
    for layer in LAYERS:
        for path in _py_files(layer):
            rel = path.relative_to(REPO_ROOT)
            for mod in _imports(path):
                if layer == "data" and mod.startswith("kernel"):
                    violations.append(f"{rel} -> {mod}")
                if layer == "services" and mod.startswith("kernel"):
                    violations.append(f"{rel} -> {mod}")
                if layer == "control" and mod.startswith("kernel.runtime"):
                    if (str(rel), mod) not in LEGACY_ALLOWED_IMPORTS:
                        violations.append(f"{rel} -> {mod}")
    assert not violations, "forbidden imports:\n" + "\n".join(sorted(violations))


def test_no_layer_cycles() -> None:
    edges: dict[str, set[str]] = {l: set() for l in LAYERS}
    for layer in LAYERS:
        for path in _py_files(layer):
            for mod in _imports(path):
                target = mod.split(".")[0]
                if target in LAYERS and target != layer:
                    edges[layer].add(target)

    temp: set[str] = set()
    perm: set[str] = set()
    cycles: list[list[str]] = []

    def visit(node: str, stack: list[str]) -> None:
        if node in perm:
            return
        if node in temp:
            start = stack.index(node)
            cycles.append(stack[start:] + [node])
            return
        temp.add(node)
        for nxt in sorted(edges[node]):
            visit(nxt, stack + [nxt])
        temp.remove(node)
        perm.add(node)

    for layer in LAYERS:
        visit(layer, [layer])

    assert not cycles, "layer cycles detected: " + "; ".join(" -> ".join(c) for c in cycles)
