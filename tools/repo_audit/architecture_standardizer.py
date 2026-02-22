"""Repository-wide architecture analysis and safe standardization planner.

This tool performs read-heavy analysis, writes migration artifacts, and applies
only low-risk compatibility-preserving cleanup steps.
"""

from __future__ import annotations

import ast
import json
from collections import Counter, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
MIGRATION_DIR = REPO_ROOT / "migration"

CANONICAL_DIRS = {
    "core",
    "agents",
    "control",
    "registry",
    "config",
    "schemas",
    "cli",
    "console",
    "db",
    "bigdata",
    "shared",
    "deploy",
    "kernel",
    "execution",
    "tests",
    "tools",
}

LAYER_MAP = {
    "core": "core",
    "agents": "agents",
    "control": "control",
    "registry": "registry",
    "config": "config",
    "schemas": "schemas",
    "cli": "cli",
    "console": "console",
    "db": "db",
    "bigdata": "bigdata",
    "shared": "shared",
    "deploy": "deploy",
    "kernel": "kernel",
    "execution": "execution",
    "tests": "tests",
    "tools": "tools",
    "os": "control",
    "aion": "control",
    "app": "control",
    "ai_registry": "registry",
    "process-analytics": "bigdata",
    "modules": "execution",
}


@dataclass
class GraphStats:
    nodes: int
    edges: int
    circular_groups: list[list[str]]
    top_centrality: list[dict[str, Any]]
    max_depth: int


def _safe_rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)).replace("\\", "/")


def _iter_files() -> list[Path]:
    ignored = {".git", "node_modules", "__pycache__", ".venv", "venv", ".pytest_cache", ".ruff_cache"}
    files: list[Path] = []
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in ignored for part in path.parts):
            continue
        files.append(path)
    return files


def classify_repo(files: list[Path]) -> dict[str, Any]:
    out: dict[str, Any] = {
        "python_modules": [],
        "rust_crates": [],
        "frontend_projects": [],
        "config_dirs": [],
        "registry_folders": [],
        "docker_files": [],
        "cli_entrypoints": [],
        "api_entrypoints": [],
        "worker_processes": [],
        "background_schedulers": [],
        "bigdata_pipelines": [],
    }
    for f in files:
        rel = _safe_rel(f)
        name = f.name
        parts = set(f.parts)
        if name.endswith(".py"):
            out["python_modules"].append(rel)
            text = f.read_text(encoding="utf-8", errors="ignore")
            if "if __name__ == \"__main__\"" in text or "argparse" in text and "cli" in rel:
                out["cli_entrypoints"].append(rel)
            if "APIRouter(" in text or "FastAPI(" in text or "Flask(" in text:
                out["api_entrypoints"].append(rel)
            if any(token in text for token in ("celery", "BackgroundTasks", "create_task(", "worker")):
                out["worker_processes"].append(rel)
            if any(token in text for token in ("schedule", "APScheduler", "cron", "crontab")):
                out["background_schedulers"].append(rel)
        if name == "Cargo.toml":
            out["rust_crates"].append(rel)
        if name == "package.json":
            out["frontend_projects"].append(rel)
        if name in {"Dockerfile"} or rel.endswith((".yml", ".yaml")) and "docker" in rel:
            out["docker_files"].append(rel)
        if any(p in {"config", "configs", "config-schemas"} for p in parts):
            out["config_dirs"].append(rel)
        if any(p in {"ai_registry", "registry"} for p in parts):
            out["registry_folders"].append(rel)
        if rel.startswith("bigdata/") or rel.startswith("process-analytics/"):
            out["bigdata_pipelines"].append(rel)

    for key in out:
        out[key] = sorted(set(out[key]))
    return out


def _module_name(py_path: Path) -> str:
    rel = py_path.relative_to(REPO_ROOT)
    no_suffix = rel.with_suffix("")
    parts = list(no_suffix.parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def build_python_graph(files: list[Path]) -> dict[str, set[str]]:
    py_files = [p for p in files if p.suffix == ".py"]
    modules = {_module_name(p): p for p in py_files}
    graph: dict[str, set[str]] = {m: set() for m in modules}

    for mod, path in modules.items():
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    target = alias.name
                    if target in modules:
                        graph[mod].add(target)
                    else:
                        prefix = target
                        while "." in prefix:
                            prefix = prefix.rsplit(".", 1)[0]
                            if prefix in modules:
                                graph[mod].add(prefix)
                                break
            elif isinstance(node, ast.ImportFrom):
                if node.module is None:
                    continue
                base = node.module
                if node.level and mod:
                    origin_parts = mod.split(".")[:-1]
                    up = max(node.level - 1, 0)
                    if up <= len(origin_parts):
                        origin_parts = origin_parts[: len(origin_parts) - up]
                    base = ".".join([*origin_parts, base]) if origin_parts else base
                if base in modules:
                    graph[mod].add(base)
                else:
                    prefix = base
                    while "." in prefix:
                        prefix = prefix.rsplit(".", 1)[0]
                        if prefix in modules:
                            graph[mod].add(prefix)
                            break
    return graph


def build_rust_graph(files: list[Path]) -> dict[str, set[str]]:
    crates: dict[str, set[str]] = {}
    crate_names: set[str] = set()
    cargo_files = [p for p in files if p.name == "Cargo.toml"]

    for cargo in cargo_files:
        text = cargo.read_text(encoding="utf-8", errors="ignore")
        name = None
        for line in text.splitlines():
            s = line.strip()
            if s.startswith("name") and "=" in s and name is None and "[package]" in text:
                name = s.split("=", 1)[1].strip().strip('"')
                break
        if name:
            crate_names.add(name)
            crates[name] = set()

    for cargo in cargo_files:
        text = cargo.read_text(encoding="utf-8", errors="ignore")
        name = None
        for line in text.splitlines():
            s = line.strip()
            if s.startswith("name") and "=" in s and name is None and "[package]" in text:
                name = s.split("=", 1)[1].strip().strip('"')
                break
        if not name:
            continue
        in_deps = False
        for line in text.splitlines():
            s = line.strip()
            if s.startswith("["):
                in_deps = s in {"[dependencies]", "[dev-dependencies]", "[build-dependencies]"}
                continue
            if in_deps and "=" in s:
                dep = s.split("=", 1)[0].strip()
                if dep in crate_names:
                    crates[name].add(dep)
    return crates


def build_frontend_graph(files: list[Path]) -> dict[str, dict[str, Any]]:
    graph: dict[str, dict[str, Any]] = {}
    for pkg in [p for p in files if p.name == "package.json"]:
        rel = _safe_rel(pkg)
        try:
            data = json.loads(pkg.read_text(encoding="utf-8", errors="ignore"))
        except json.JSONDecodeError:
            continue
        graph[rel] = {
            "name": data.get("name", rel),
            "dependencies": sorted((data.get("dependencies") or {}).keys()),
            "devDependencies": sorted((data.get("devDependencies") or {}).keys()),
            "scripts": sorted((data.get("scripts") or {}).keys()),
        }
    return graph


def strongly_connected_components(graph: dict[str, set[str]]) -> list[list[str]]:
    index = 0
    idx: dict[str, int] = {}
    low: dict[str, int] = {}
    stack: list[str] = []
    on_stack: set[str] = set()
    out: list[list[str]] = []

    def visit(v: str) -> None:
        nonlocal index
        idx[v] = index
        low[v] = index
        index += 1
        stack.append(v)
        on_stack.add(v)

        for w in graph.get(v, set()):
            if w not in idx:
                visit(w)
                low[v] = min(low[v], low[w])
            elif w in on_stack:
                low[v] = min(low[v], idx[w])

        if low[v] == idx[v]:
            comp: list[str] = []
            while True:
                w = stack.pop()
                on_stack.remove(w)
                comp.append(w)
                if w == v:
                    break
            if len(comp) > 1:
                out.append(sorted(comp))

    for n in graph:
        if n not in idx:
            visit(n)
    return out


def centrality_and_depth(graph: dict[str, set[str]]) -> tuple[list[dict[str, Any]], int]:
    indeg = Counter()
    outdeg = Counter({k: len(v) for k, v in graph.items()})
    for src, dsts in graph.items():
        for dst in dsts:
            indeg[dst] += 1
            indeg[src] += 0

    top = []
    for node in graph:
        top.append(
            {
                "module": node,
                "fan_in": indeg[node],
                "fan_out": outdeg[node],
                "centrality": indeg[node] + outdeg[node],
            }
        )
    top.sort(key=lambda x: x["centrality"], reverse=True)

    max_depth = 0
    for start in graph:
        q: deque[tuple[str, int]] = deque([(start, 0)])
        seen = {start}
        while q:
            node, depth = q.popleft()
            max_depth = max(max_depth, depth)
            for nxt in graph.get(node, set()):
                if nxt in seen:
                    continue
                seen.add(nxt)
                q.append((nxt, depth + 1))
    return top[:10], max_depth


def cross_layer_violations(py_graph: dict[str, set[str]]) -> list[dict[str, str]]:
    violations: list[dict[str, str]] = []

    def layer_of(module: str) -> str:
        root = module.split(".", 1)[0]
        return LAYER_MAP.get(root, "unknown")

    for src, deps in py_graph.items():
        src_layer = layer_of(src)
        for dst in deps:
            dst_layer = layer_of(dst)
            if src_layer == "control" and dst_layer == "cli":
                violations.append({"type": "control_depends_on_cli", "src": src, "dst": dst})
            if src_layer == "agents" and dst_layer == "registry" and "registry" not in dst:
                violations.append({"type": "agent_reads_registry_directly", "src": src, "dst": dst})
            if src_layer == "bigdata" and dst_layer == "control":
                violations.append({"type": "bigdata_depends_on_control", "src": src, "dst": dst})
    return violations


def env_and_registry_smells(files: list[Path]) -> dict[str, int]:
    env_count = 0
    registry_reads = 0
    schema_dups = 0
    schema_names: Counter[str] = Counter()

    for p in files:
        if p.suffix in {".py", ".ts", ".js", ".sh", ".ps1"}:
            text = p.read_text(encoding="utf-8", errors="ignore")
            env_count += text.count("os.getenv(") + text.count("process.env")
            registry_reads += text.count("registry.lock") + text.count("ai_registry")
        if p.suffix == ".json" and "schema" in p.name.lower():
            schema_names[p.name] += 1

    schema_dups = sum(1 for _, c in schema_names.items() if c > 1)
    return {
        "env_access_points": env_count,
        "direct_registry_reads": registry_reads,
        "duplicated_schema_filenames": schema_dups,
    }


def orphan_dirs() -> list[str]:
    ignored = {".git", "node_modules", "__pycache__", ".pytest_cache", ".ruff_cache"}
    out = []
    for d in sorted([p for p in REPO_ROOT.iterdir() if p.is_dir()]):
        if d.name in ignored:
            continue
        if d.name not in CANONICAL_DIRS and d.name not in {"docs", "scripts", "os", "aion", "app", "services", "profiles", "models", "modules", "configs", "kernel-multitenant", "omertaos", "aionos_core", "aionos_control", "ai_registry", "process-analytics", "integrations", "packages"}:
            out.append(d.name)
    return out


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    MIGRATION_DIR.mkdir(parents=True, exist_ok=True)
    files = _iter_files()

    inventory = classify_repo(files)
    py_graph = build_python_graph(files)
    rust_graph = build_rust_graph(files)
    fe_graph = build_frontend_graph(files)

    py_cycles = strongly_connected_components(py_graph)
    py_top, py_depth = centrality_and_depth(py_graph)
    violations = cross_layer_violations(py_graph)
    smells = env_and_registry_smells(files)

    py_edges = sum(len(v) for v in py_graph.values())
    coupling = round(py_edges / max(len(py_graph), 1), 3)

    metrics = {
        "python": {
            "modules": len(py_graph),
            "edges": py_edges,
            "coupling_score": coupling,
            "circular_groups": len(py_cycles),
            "max_depth": py_depth,
            "top_centrality": py_top,
        },
        "rust": {
            "crates": len(rust_graph),
            "edges": sum(len(v) for v in rust_graph.values()),
        },
        "frontend": {
            "projects": len(fe_graph),
        },
        "violations": {
            "cross_layer": len(violations),
        },
        "smells": smells,
        "orphans": orphan_dirs(),
    }

    write_json(MIGRATION_DIR / "repo_inventory_full.json", inventory)
    write_json(MIGRATION_DIR / "dependency_graph_python_full.json", {k: sorted(v) for k, v in py_graph.items()})
    write_json(MIGRATION_DIR / "dependency_graph_rust_full.json", {k: sorted(v) for k, v in rust_graph.items()})
    write_json(MIGRATION_DIR / "dependency_graph_frontend_full.json", fe_graph)
    write_json(MIGRATION_DIR / "cross_layer_violations_full.json", violations)
    write_json(MIGRATION_DIR / "metrics_full_after.json", metrics)

    plan = {
        "derived_from": "tools/repo_audit/architecture_standardizer.py",
        "safe_moves": [
            {
                "status": "already_applied",
                "from": "repo root setup files",
                "to": "deploy/scripts + deploy/compose with root wrappers",
                "reason": "align with canonical /deploy while preserving compatibility",
            }
        ],
        "next_moves": [
            "Migrate remaining root operational scripts into deploy/scripts with wrapper shims.",
            "Converge os/control + control packages behind canonical control namespace.",
            "Consolidate duplicate schema names under /schemas with compatibility aliases.",
        ],
    }
    write_json(MIGRATION_DIR / "migration_plan_derived.json", plan)

    report = [
        "# Full Architecture Standardization Report",
        "",
        "## Scope",
        "- Full repository scan (Python, Rust, frontend, config, deploy, registry).",
        "- Multi-language dependency graphs generated.",
        "- Cross-layer rules evaluated against canonical architecture.",
        "",
        "## Key Metrics",
        f"- Python modules: {metrics['python']['modules']}",
        f"- Python edges: {metrics['python']['edges']}",
        f"- Python coupling score: {metrics['python']['coupling_score']}",
        f"- Circular import groups: {metrics['python']['circular_groups']}",
        f"- Max dependency depth: {metrics['python']['max_depth']}",
        f"- Rust crates: {metrics['rust']['crates']}",
        f"- Frontend projects: {metrics['frontend']['projects']}",
        f"- Cross-layer violations: {metrics['violations']['cross_layer']}",
        "",
        "## Top 10 Centrality (Python)",
    ]
    for row in metrics["python"]["top_centrality"]:
        report.append(
            f"- {row['module']}: centrality={row['centrality']} (in={row['fan_in']}, out={row['fan_out']})"
        )

    report += [
        "",
        "## Smells",
        f"- Env scattered access points: {smells['env_access_points']}",
        f"- Direct registry read patterns: {smells['direct_registry_reads']}",
        f"- Duplicated schema filenames: {smells['duplicated_schema_filenames']}",
        "",
        "## Orphan directories",
    ]
    if metrics["orphans"]:
        report += [f"- {name}" for name in metrics["orphans"]]
    else:
        report.append("- None detected at repository root.")

    report += [
        "",
        "## Safe refactoring actions",
        "- No destructive bulk move executed.",
        "- Existing deploy-oriented setup relocation retained as compatibility-preserving standardization step.",
        "",
        "## Artifacts",
        "- migration/repo_inventory_full.json",
        "- migration/dependency_graph_python_full.json",
        "- migration/dependency_graph_rust_full.json",
        "- migration/dependency_graph_frontend_full.json",
        "- migration/cross_layer_violations_full.json",
        "- migration/metrics_full_after.json",
        "- migration/migration_plan_derived.json",
    ]
    (MIGRATION_DIR / "standardization_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    print(json.dumps({"ok": True, "metrics": metrics}, indent=2))


if __name__ == "__main__":
    main()
