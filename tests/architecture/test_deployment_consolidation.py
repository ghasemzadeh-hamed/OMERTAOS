from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_canonical_deployment_owners_exist() -> None:
    required = (
        "deploy/native/env/omertaos.env.example",
        "deploy/native/scripts/install.sh",
        "deploy/native/scripts/run.sh",
        "deploy/native/systemd/omertaos.target",
        "deploy/docker/compose/quickstart.yml",
        "deploy/docker/compose/local.yml",
        "deploy/docker/compose/full.yml",
        "deploy/docker/scripts/install.sh",
        "deploy/docker/scripts/run.sh",
        "deploy/kubernetes/control-deployment.yaml",
        "deploy/kubernetes/gateway-deployment.yaml",
    )

    missing = [path for path in required if not (REPO_ROOT / path).is_file()]
    assert not missing, f"missing canonical deployment assets: {missing}"


def test_root_entrypoints_are_thin_canonical_wrappers() -> None:
    expected_targets = {
        "install.sh": "deploy/native/scripts/install.sh",
        "install.ps1": "deploy/docker/scripts/install.ps1",
        "run.sh": "deploy/native/scripts/run.sh",
        "run.ps1": "deploy/docker/scripts/run.ps1",
        "quick-install.sh": "deploy/docker/scripts/install.sh",
        "quick-install.ps1": "deploy/docker/scripts/install.ps1",
        "uninstall.sh": "deploy/docker/scripts/uninstall.sh",
        "uninstall.ps1": "deploy/docker/compose/full.yml",
    }

    for wrapper, target in expected_targets.items():
        text = (REPO_ROOT / wrapper).read_text(encoding="utf-8")
        assert target in text, f"{wrapper} must delegate to {target}"
        assert len(text.splitlines()) <= 16, f"{wrapper} contains deployment logic"


def test_root_compose_compatibility_payloads_are_retired() -> None:
    for path in (
        "docker-compose.quickstart.yml",
        "docker-compose.local.yml",
        "docker-compose.yml",
        "docker-compose.obsv.yml",
        "docker-compose.vllm.yml",
    ):
        assert not (REPO_ROOT / path).exists(), f"legacy Compose payload remains: {path}"


def test_active_deployment_consumers_do_not_target_legacy_roots() -> None:
    active_files = (
        "Makefile",
        "README.md",
        "deploy/README.md",
        "docs/local-quickstart.md",
        "deploy/CAPO/scripts/smoke-test.sh",
        "deploy/CAPO/tests/contract-tests.ps1",
        "deploy/native/scripts/smoke-test.sh",
    )
    forbidden = (
        "execution/compose",
        "execution/k8s",
        "execution/systemd",
        "infra/linux",
        "core/systemd",
        "docker/compose.catalog.yml",
        "deploy/k8s/",
    )

    for path in active_files:
        text = (REPO_ROOT / path).read_text(encoding="utf-8")
        hits = [legacy for legacy in forbidden if legacy in text]
        assert not hits, f"{path} still targets legacy deployment paths: {hits}"


def test_console_compose_services_only_receive_gateway_boundary() -> None:
    forbidden = {"CONTROL_URL", "AION_CONTROL_URL", "AION_CONTROL_BASE_URL", "NEXT_PUBLIC_CONTROL_URL", "RUNTIME_URL"}
    for relative in ("deploy/docker/compose/quickstart.yml", "deploy/docker/compose/local.yml"):
        compose = yaml.safe_load((REPO_ROOT / relative).read_text(encoding="utf-8"))
        services = compose.get("services", {})
        for service_name in ("console", "install"):
            if service_name not in services:
                continue
            environment = services[service_name].get("environment", {})
            keys = set(environment) if isinstance(environment, dict) else {
                item.split("=", 1)[0] for item in environment
            }
            hits = sorted(keys & forbidden)
            assert not hits, f"{relative} {service_name} receives direct Control/Runtime settings: {hits}"


def test_native_rollback_is_previewable_and_preserves_state() -> None:
    rollback = (REPO_ROOT / "deploy/native/scripts/rollback.sh").read_text(encoding="utf-8")
    required = (
        "--dry-run",
        "systemctl stop omertaos.target",
        "/opt/omertaos/previous",
        "sha256sum --check",
        "no database downgrade was attempted",
    )
    assert all(token in rollback for token in required)

    lowered = rollback.lower()
    forbidden = ("rm -rf", "drop table", "drop database", "truncate table", "docker volume rm")
    assert not [token for token in forbidden if token in lowered]
