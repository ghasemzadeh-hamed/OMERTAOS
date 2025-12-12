"""Generate repository inventory for OMERTAOS."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DOC_PATH = REPO_ROOT / "docs" / "INVENTORY.md"


def find_subprojects() -> List[str]:
    roots = []
    for entry in REPO_ROOT.iterdir():
        if entry.is_dir() and any((entry / marker).exists() for marker in ["package.json", "pyproject.toml", "Dockerfile", "setup.py"]):
            roots.append(entry.name)
    roots.sort()
    return roots


def find_package_managers() -> List[str]:
    markers = ["package.json", "pnpm-lock.yaml", "yarn.lock", "requirements.txt", "poetry.lock", "pyproject.toml", "Makefile"]
    found = set()
    for marker in markers:
        for path in REPO_ROOT.rglob(marker):
            if "node_modules" in path.parts:
                continue
            found.add(str(path.relative_to(REPO_ROOT)))
    return sorted(found)


def load_compose_ports() -> Dict[str, List[str]]:
    ports: Dict[str, List[str]] = {}
    for compose in REPO_ROOT.glob("docker-compose*.yml"):
        with compose.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
        services = data.get("services", {}) if isinstance(data, dict) else {}
        for name, svc in services.items():
            for port in svc.get("ports", []) or []:
                ports.setdefault(str(compose.name), []).append(str(port))
    return ports


def load_env_keys() -> List[str]:
    env_files = [".env.example", "dev.env", "config/.env.example"]
    keys = set()
    for rel in env_files:
        path = REPO_ROOT / rel
        if not path.exists():
            continue
        for line in path.read_text().splitlines():
            if not line or line.startswith("#") or "=" not in line:
                continue
            keys.add(line.split("=", 1)[0].strip())
    return sorted(keys)


def write_inventory():
    subprojects = find_subprojects()
    managers = find_package_managers()
    ports = load_compose_ports()
    env_keys = load_env_keys()

    lines = ["# Repository Inventory", "", "## Subprojects", ""]
    for item in subprojects:
        lines.append(f"- {item}")

    lines += ["", "## Package/Build Markers", ""]
    for marker in managers:
        lines.append(f"- {marker}")

    lines += ["", "## Runtime Ports (from docker-compose*.yml)", ""]
    for file, mappings in sorted(ports.items()):
        lines.append(f"- **{file}**")
        for mapping in mappings:
            lines.append(f"  - {mapping}")

    lines += ["", "## Environment Keys", ""]
    for key in env_keys:
        lines.append(f"- {key}")

    DOC_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps({
        "subprojects": subprojects,
        "managers": managers,
        "ports": ports,
        "env_keys": env_keys,
        "doc": str(DOC_PATH)
    }, indent=2))


if __name__ == "__main__":
    write_inventory()
