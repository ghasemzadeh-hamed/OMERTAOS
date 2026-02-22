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


def is_symlink(path: str) -> bool:
    return (REPO_ROOT / path).is_symlink()


def is_symlink_to(path: str, target: str) -> bool:
    source = REPO_ROOT / path
    if not source.is_symlink():
        return False
    return source.resolve() == (REPO_ROOT / target).resolve()


def collect_findings() -> list[Finding]:
    findings: list[Finding] = []

    migrated_legacy_roots = {
        "v1": "schemas/protos/python/v1",
        "worker": "execution/worker",
        "ui": "console/ui",
        "protos": "schemas/protos",
        "llm": "shared/llm",
        "process-analytics": "bigdata/process_analytics",
    }
    for root, target in migrated_legacy_roots.items():
        if not exists(root):
            continue
        if is_symlink_to(root, target):
            findings.append(
                Finding(
                    id=f"legacy-compat:{root}",
                    severity="info",
                    message=f"Legacy root '{root}' is now a compatibility symlink.",
                    remediation=f"Update callers to '{target}' and remove '{root}' after migration window.",
                )
            )
        else:
            findings.append(
                Finding(
                    id=f"legacy-root:{root}",
                    severity="warn",
                    message=f"Legacy root '{root}' is still present.",
                    remediation="Move/alias content under canonical roots (control, console, schemas, bigdata, deploy).",
                )
            )

    if exists("config") and exists("configs"):
        if is_symlink_to("configs/systemd", "config/systemd") and is_symlink_to("configs/windows", "config/windows"):
            findings.append(
                Finding(
                    id="config-compatibility-symlink",
                    severity="info",
                    message="configs/{systemd,windows} are compatibility symlinks to config/.",
                    remediation="Keep until external callers fully migrate to config/ paths, then remove configs/ symlinks.",
                )
            )
        else:
            findings.append(
                Finding(
                    id="duplicate-config-roots",
                    severity="error",
                    message="Both 'config/' and 'configs/' exist.",
                    remediation="Keep runtime config in config/ and migrate installer/deployment templates to deploy/ + docs references.",
                )
            )

    if exists("models") and exists("registry/models"):
        if is_symlink_to("models", "registry/models"):
            findings.append(
                Finding(
                    id="models-compatibility-symlink",
                    severity="info",
                    message="models/ now points to registry/models as compatibility path.",
                    remediation="Migrate remaining references to registry/models and retire models/ symlink later.",
                )
            )

    if exists("ci") and exists("deploy/ci"):
        findings.append(
            Finding(
                id="ci-layout",
                severity="info",
                message="ci/ is retained as a wrapper while deploy/ci is canonical.",
                remediation="Move direct callers to deploy/ci and delete wrapper files in ci/ in a future cleanup.",
            )
        )

    if exists("scripts") and exists("deploy/scripts"):
        findings.append(
            Finding(
                id="scripts-split",
                severity="info",
                message="Both scripts/ (dev) and deploy/scripts (ops) are present by design.",
                remediation="Keep boundaries documented; avoid duplicating script logic across both roots.",
            )
        )

    if exists("core/systemd") and exists("deploy/systemd"):
        service_links = [
            is_symlink_to("core/systemd/aion-control.service", "deploy/systemd/aion-control.service"),
            is_symlink_to("core/systemd/aion-gateway.service", "deploy/systemd/aion-gateway.service"),
            is_symlink_to("core/systemd/aion-console.service", "deploy/systemd/aion-console.service"),
        ]
        severity = "info" if all(service_links) else "warn"
        findings.append(
            Finding(
                id="systemd-layout",
                severity=severity,
                message="core/systemd and deploy/systemd both exist.",
                remediation="Keep deploy/systemd canonical; preserve core/systemd only as compatibility links and target units.",
            )
        )

    if exists("core/windows") and is_symlink_to("core/windows", "deploy/windows/core"):
        findings.append(
            Finding(
                id="windows-core-compat",
                severity="info",
                message="core/windows is now a compatibility symlink to deploy/windows/core.",
                remediation="Use deploy/windows/core as canonical path.",
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
