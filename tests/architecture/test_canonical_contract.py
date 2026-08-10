from __future__ import annotations

import ast
import re
import shutil
import subprocess  # nosec B404 - invokes only the resolved local Git executable
from pathlib import Path

from tests.architecture.legacy_contract import (
    HISTORICAL_EVIDENCE_ROOTS,
    LEGACY_IMPORT_PREFIXES,
    LEGACY_ROOTS,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
CANONICAL_PYTHON_ROOTS = ("control", "data", "registry", "policies", "shared", "integrations")
CANONICAL_SOURCE_ROOTS = (
    "console",
    "gateway",
    "control",
    "runtime-daemon",
    "data",
    "registry",
    "policies",
    "shared",
    "integrations",
)
ACTIVE_REFERENCE_ROOTS = CANONICAL_SOURCE_ROOTS + ("deploy", "scripts")


def _source_files(root: Path, suffixes: tuple[str, ...]) -> list[Path]:
    ignored = {"node_modules", ".next", "dist", "target", "__pycache__"}
    if not root.exists():
        return []
    return [
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix in suffixes and not ignored.intersection(path.parts)
    ]


def _python_imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    return imports


def test_canonical_python_has_no_legacy_imports() -> None:
    violations: list[str] = []
    for root_name in CANONICAL_PYTHON_ROOTS:
        for path in _source_files(REPO_ROOT / root_name, (".py",)):
            for module in _python_imports(path):
                if module in LEGACY_IMPORT_PREFIXES or module.startswith(
                    tuple(f"{prefix}." for prefix in LEGACY_IMPORT_PREFIXES)
                ):
                    violations.append(f"{path.relative_to(REPO_ROOT)} -> {module}")
    assert not violations, "canonical Python imported legacy modules:\n" + "\n".join(sorted(violations))


def _tracked_paths() -> tuple[str, ...]:
    git = shutil.which("git")
    assert git, "git executable is required for the tracked-root contract"
    result = subprocess.run(  # nosec B603 - fixed Git subcommand and arguments
        [git, "ls-files", "-z"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
    )
    return tuple(
        path.decode("utf-8").replace("\\", "/")
        for path in result.stdout.split(b"\0")
        if path
    )


def test_no_retired_root_is_tracked() -> None:
    tracked_roots = {path.split("/", 1)[0] for path in _tracked_paths() if "/" in path}
    violations = sorted(tracked_roots.intersection(LEGACY_ROOTS))
    assert not violations, "retired top-level roots are still tracked: " + ", ".join(violations)


def test_historical_evidence_allowlist_is_documentation_scoped() -> None:
    assert HISTORICAL_EVIDENCE_ROOTS
    for root in HISTORICAL_EVIDENCE_ROOTS:
        assert root.startswith("docs/")
        assert (REPO_ROOT / root).is_dir()


def test_active_source_has_no_legacy_runtime_path_reference() -> None:
    legacy_path = rf"(?:{'|'.join(re.escape(root) for root in LEGACY_ROOTS)})(?:/|\\\\)"
    import_patterns = (
        re.compile(rf"(?:from|require\(|import\()[\s\"'][^\"']*{legacy_path}"),
        re.compile(rf"\bpath\s*=\s*[\"'][^\"']*{legacy_path}"),
        re.compile(
            rf"\buse\s+(?:{'|'.join(re.escape(prefix) for prefix in LEGACY_IMPORT_PREFIXES)})(?::|;)"
        ),
    )
    violations: list[str] = []
    suffixes = (
        ".cjs",
        ".js",
        ".json",
        ".mjs",
        ".ps1",
        ".py",
        ".rs",
        ".sh",
        ".toml",
        ".ts",
        ".tsx",
        ".yaml",
        ".yml",
    )
    for root_name in ACTIVE_REFERENCE_ROOTS:
        for path in _source_files(REPO_ROOT / root_name, suffixes):
            source = path.read_text(encoding="utf-8")
            if any(pattern.search(source) for pattern in import_patterns):
                violations.append(str(path.relative_to(REPO_ROOT)))
    assert not violations, "canonical source referenced a legacy import path: " + ", ".join(
        sorted(violations)
    )


def test_gateway_has_no_domain_database_dependency() -> None:
    forbidden = re.compile(
        r"(?:from|require\()[\s\"']+(?:@prisma/client|prisma|typeorm|sequelize|mongoose|mongodb|pg|postgres|data/|database/|db/)",
        re.IGNORECASE,
    )
    violations = [
        str(path.relative_to(REPO_ROOT))
        for path in _source_files(REPO_ROOT / "gateway" / "src", (".ts", ".tsx", ".js", ".mjs"))
        if forbidden.search(path.read_text(encoding="utf-8"))
    ]
    assert not violations, "Gateway accessed domain persistence directly: " + ", ".join(sorted(violations))


def test_control_has_no_host_execution() -> None:
    forbidden_imports = ("subprocess", "multiprocessing", "pty", "ctypes")
    forbidden_calls = re.compile(r"\b(?:os\.(?:system|popen|spawn\w*)|asyncio\.create_subprocess_\w+)\s*\(")
    violations: list[str] = []
    for path in _source_files(REPO_ROOT / "control", (".py",)):
        imports = _python_imports(path)
        source = path.read_text(encoding="utf-8")
        if any(
            module == prefix or module.startswith(f"{prefix}.")
            for module in imports
            for prefix in forbidden_imports
        ):
            violations.append(str(path.relative_to(REPO_ROOT)))
        elif forbidden_calls.search(source):
            violations.append(str(path.relative_to(REPO_ROOT)))
    assert not violations, "Control performed host execution directly: " + ", ".join(sorted(violations))


def test_structure_migration_gate() -> None:
    violations = [root for root in LEGACY_ROOTS if (REPO_ROOT / root).exists()]
    direct_console_tokens = (
        "CONTROL_URL",
        "AION_CONTROL_URL",
        "NEXT_PUBLIC_CONTROL_URL",
        "RUNTIME_URL",
        "http://localhost:8000",
        "http://control:8000",
    )
    for path in _source_files(REPO_ROOT / "console", (".ts", ".tsx", ".js", ".mjs", ".json")):
        source = path.read_text(encoding="utf-8")
        if any(token in source for token in direct_console_tokens):
            violations.append(f"direct Console boundary: {path.relative_to(REPO_ROOT)}")
    assert not violations, (
        "Structure migration regressed from its canonical root contract:\n"
        + "\n".join(sorted(violations))
    )
