from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ALLOWED = {
    Path("kernel/sandbox/container_executor.py"),
    Path("kernel/kernel_adapter/linux_adapter.py"),
}

LEGACY_ALLOWED = {
    Path("control/install_runner.py"),
    Path("control/os/api/provisioner.py"),
    Path("control/os/api/services.py"),
    Path("control/os/api/update.py"),
    Path("control/os/routes/admin_onboarding.py"),
    Path("control/os/routes/models.py"),
    Path("control/tools/shell_tool.py"),
}


def _py_files() -> list[Path]:
    roots = ["kernel", "control", "data", "services", "execution", "domain", "interface", "shared"]
    out: list[Path] = []
    for root in roots:
        p = REPO_ROOT / root
        if p.exists():
            out.extend([f for f in p.rglob("*.py") if "__pycache__" not in f.parts])
    return out


def test_subprocess_usage_limited_to_adapter_and_sandbox() -> None:
    violations: list[str] = []
    for path in _py_files():
        rel = path.relative_to(REPO_ROOT)
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        has_subprocess = False
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                if any(alias.name == "subprocess" for alias in node.names):
                    has_subprocess = True
            if isinstance(node, ast.ImportFrom) and node.module == "subprocess":
                has_subprocess = True
        if has_subprocess and rel not in ALLOWED and rel not in LEGACY_ALLOWED:
            violations.append(str(rel))
    assert not violations, "subprocess imports outside sandbox/adapter: " + ", ".join(sorted(violations))
