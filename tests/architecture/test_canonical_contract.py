from __future__ import annotations

import ast
import re
from pathlib import Path

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
LEGACY_IMPORT_PREFIXES = ("control_plane", "rust_runtime", "database", "db")
LEGACY_ROOTS = (
    "control-plane",
    "rust-runtime",
    "database",
    "db",
    "models",
    "orchestration",
    "eventbus",
    "observability",
)


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


def test_canonical_source_has_no_legacy_path_imports() -> None:
    legacy_path = r"(?:control-plane|rust-runtime|database|db)(?:/|\\)"
    import_patterns = (
        re.compile(rf"(?:from|require\(|import\()[\s\"'][^\"']*{legacy_path}"),
        re.compile(rf"\bpath\s*=\s*[\"'][^\"']*{legacy_path}"),
        re.compile(r"\buse\s+(?:control_plane|rust_runtime|database|db)(?::|;)"),
    )
    violations: list[str] = []
    suffixes = (".ts", ".tsx", ".js", ".mjs", ".rs", ".toml")
    for root_name in CANONICAL_SOURCE_ROOTS:
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
    direct_console_tokens = ("CONTROL_URL", "AION_CONTROL_URL", "NEXT_PUBLIC_CONTROL_URL", "RUNTIME_URL")
    for path in _source_files(REPO_ROOT / "console", (".ts", ".tsx", ".js", ".mjs")):
        source = path.read_text(encoding="utf-8")
        if any(token in source for token in direct_console_tokens):
            violations.append(f"direct Console boundary: {path.relative_to(REPO_ROOT)}")
    assert not violations, (
        "Structure migration is incomplete; this gate must remain red until S2-S5 resolve:\n"
        + "\n".join(sorted(violations))
    )
