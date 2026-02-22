"""Detect known repository structure inconsistencies and print a remediation report."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Finding:
    id: str
    severity: str
    message: str
    remediation: str


def exists(path: str) -> bool:
    return (REPO_ROOT / path).exists()


def collect_findings() -> list[Finding]:
    findings: list[Finding] = []

    legacy_roots = ["v1", "worker", "ui", "protos", "llm", "process-analytics"]
    for root in legacy_roots:
        if exists(root):
            findings.append(
                Finding(
                    id=f"legacy-root:{root}",
                    severity="warn",
                    message=f"Legacy root '{root}' is still present.",
                    remediation="Move/alias content under canonical roots (control, console, schemas, bigdata, deploy).",
                )
            )

    if exists("config") and exists("configs"):
        findings.append(
            Finding(
                id="duplicate-config-roots",
                severity="error",
                message="Both 'config/' and 'configs/' exist.",
                remediation="Keep runtime config in config/ and migrate installer/deployment templates to deploy/ + docs references.",
            )
        )

    if exists("models") and exists("control/models"):
        findings.append(
            Finding(
                id="duplicate-model-roots",
                severity="warn",
                message="Both 'models/' and 'control/models/' exist.",
                remediation="Define one source of truth (registry/models or control/models) and keep the other as compatibility wrappers only.",
            )
        )

    if exists("ci") and exists("deploy/ci"):
        findings.append(
            Finding(
                id="duplicate-ci-roots",
                severity="warn",
                message="Both 'ci/' and 'deploy/ci/' exist.",
                remediation="Use deploy/ci as canonical; keep ci/ as thin compatibility wrappers or remove after migration.",
            )
        )

    if exists("scripts") and exists("deploy/scripts"):
        findings.append(
            Finding(
                id="duplicate-script-roots",
                severity="warn",
                message="Both 'scripts/' and 'deploy/scripts/' exist.",
                remediation="Use scripts/ for developer workflows and deploy/scripts for operations-only scripts; document boundary clearly.",
            )
        )

    if exists("core/systemd") and exists("deploy/systemd"):
        findings.append(
            Finding(
                id="duplicate-systemd-roots",
                severity="warn",
                message="Both 'core/systemd/' and 'deploy/systemd/' exist.",
                remediation="Consolidate service units under deploy/systemd and keep references in core/ only when coupled to source artifacts.",
            )
        )

    if not exists("config/systemd"):
        findings.append(
            Finding(
                id="missing-config-systemd",
                severity="info",
                message="No 'config/systemd/' directory found (possible typo such as sustemd).",
                remediation="If needed, create config/systemd/ and migrate any misplaced service templates there.",
            )
        )

    if not exists("config/windows"):
        findings.append(
            Finding(
                id="missing-config-windows",
                severity="info",
                message="No 'config/windows/' directory found.",
                remediation="If Windows bootstrap files are required, keep them under deploy/ci/windows or deploy/scripts and remove stale references.",
            )
        )

    if exists("kernel/profiles") and not any((REPO_ROOT / "kernel/profiles").glob("*.md")):
        findings.append(
            Finding(
                id="kernel-profiles-undocumented",
                severity="warn",
                message="kernel/profiles exists without a local markdown index.",
                remediation="Add a README.md documenting profile ownership, completeness, and migration status.",
            )
        )

    return findings


def main() -> int:
    findings = collect_findings()
    print("# Repository structure consistency report")
    print(f"root: {REPO_ROOT}")
    print(f"findings: {len(findings)}")

    severity_order = {"error": 0, "warn": 1, "info": 2}
    for finding in sorted(findings, key=lambda item: severity_order[item.severity]):
        print(f"- [{finding.severity.upper()}] {finding.id}: {finding.message}")
        print(f"  -> {finding.remediation}")

    return 1 if any(item.severity == "error" for item in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
