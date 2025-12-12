"""Compare documentation claims with code truth for ports and env keys."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, Set

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = REPO_ROOT / "docs" / "DOCS_PARITY_REPORT.md"


PORT_PATTERN = re.compile(r"\b(\d{4,5})\b")
ENV_PATTERN = re.compile(r"\b[A-Z][A-Z0-9_]{2,}\b")


def gather_doc_claims() -> Dict[str, Set[str]]:
    ports: Set[str] = set()
    envs: Set[str] = set()
    for path in REPO_ROOT.rglob("*.md"):
        if "node_modules" in str(path):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        ports.update(PORT_PATTERN.findall(text))
        envs.update(ENV_PATTERN.findall(text))
    return {"ports": ports, "envs": envs}


def gather_code_truth() -> Dict[str, Set[str]]:
    ports: Set[str] = set()
    envs: Set[str] = set()
    for compose in REPO_ROOT.glob("docker-compose*.yml"):
        data = yaml.safe_load(compose.read_text())
        services = data.get("services", {}) if isinstance(data, dict) else {}
        for svc in services.values():
            for port in svc.get("ports", []) or []:
                for token in PORT_PATTERN.findall(str(port)):
                    ports.add(token)
    for env_file in [".env.example", "dev.env", "config/.env.example"]:
        path = REPO_ROOT / env_file
        if not path.exists():
            continue
        for line in path.read_text().splitlines():
            if not line or line.startswith("#") or "=" not in line:
                continue
            envs.add(line.split("=", 1)[0].strip())
    return {"ports": ports, "envs": envs}


def write_report():
    docs = gather_doc_claims()
    code = gather_code_truth()
    missing_in_docs_ports = sorted(code["ports"] - docs["ports"])
    missing_in_docs_envs = sorted(code["envs"] - docs["envs"])
    stale_ports = sorted(docs["ports"] - code["ports"])
    stale_envs = sorted(docs["envs"] - code["envs"])

    lines = ["# Docs Parity Report", "", "## Summary", "", f"- Ports claimed in code: {len(code['ports'])}", f"- Ports claimed in docs: {len(docs['ports'])}", f"- Env keys in code: {len(code['envs'])}", f"- Env keys in docs: {len(docs['envs'])}"]

    lines += ["", "## Missing in Docs (must be documented)", ""]
    lines.append("### Ports")
    for port in missing_in_docs_ports:
        lines.append(f"- {port}")
    lines.append("### Env Vars")
    for key in missing_in_docs_envs:
        lines.append(f"- {key}")

    lines += ["", "## Stale in Docs (not found in code)", ""]
    lines.append("### Ports")
    for port in stale_ports:
        lines.append(f"- {port}")
    lines.append("### Env Vars")
    for key in stale_envs:
        lines.append(f"- {key}")

    lines += ["", "## How to Reproduce", "", "```bash", "python tools/repo_audit/doc_truth_check.py", "```", ""]

    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({
        "missing_ports": missing_in_docs_ports,
        "missing_envs": missing_in_docs_envs,
        "stale_ports": stale_ports,
        "stale_envs": stale_envs,
        "report": str(REPORT_PATH),
    }, indent=2))


if __name__ == "__main__":
    write_report()
