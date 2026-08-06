from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CANONICAL_ROOT = REPO_ROOT / "integrations" / "windows-agentic-bridge"
LEGACY_ROOT = REPO_ROOT / "execution" / "windows-agentic-bridge"


def _files(root: Path) -> dict[str, Path]:
    return {
        path.relative_to(root).as_posix(): path
        for path in root.rglob("*")
        if path.is_file() and not {"node_modules", "dist"}.intersection(path.relative_to(root).parts)
    }


def test_bridge_legacy_tree_is_retired_after_canonical_inventory_check() -> None:
    canonical = _files(CANONICAL_ROOT)
    assert len(canonical) == 41
    assert not LEGACY_ROOT.exists()


def test_bridge_ownership_and_active_references_are_canonical() -> None:
    canonical_readme = (CANONICAL_ROOT / "README.md").read_text(encoding="utf-8")

    assert "Canonical owner: `integrations/windows-agentic-bridge/`" in canonical_readme
    assert not LEGACY_ROOT.exists()

    active_roots = (REPO_ROOT / "console" / "app" / "integrations" / "windows-bridge", CANONICAL_ROOT)
    for root in active_roots:
        for path in root.rglob("*"):
            relative = path.relative_to(root)
            generated = {"node_modules", "dist"}.intersection(relative.parts)
            if (
                path.is_file()
                and not generated
                and path.suffix.lower() in {".ts", ".tsx", ".js", ".json", ".md", ".ps1", ".sh"}
            ):
                source = path.read_text(encoding="utf-8")
                assert "execution/windows-agentic-bridge" not in source, path


def test_bridge_calls_gateway_only_and_uses_versioned_task_routes() -> None:
    config = (CANONICAL_ROOT / "bridge-server" / "src" / "config.ts").read_text(encoding="utf-8")
    client = (CANONICAL_ROOT / "bridge-server" / "src" / "omertaClient.ts").read_text(encoding="utf-8")
    env_example = (CANONICAL_ROOT / "bridge-server" / ".env.example").read_text(encoding="utf-8")
    ui_config = (
        CANONICAL_ROOT / "bridge-ui" / "src" / "components" / "OmertaConfigForm.tsx"
    ).read_text(encoding="utf-8")

    assert "controlUrl" not in config
    assert "OMERTA_CONTROL_URL" not in env_example
    assert "OMERTA_GATEWAY_URL=http://localhost:8080" in env_example
    assert client.count("axios.create(") == 1
    assert "this.control" not in client
    assert "config.controlUrl" not in client
    assert "this.gateway.get('/health')" in client
    assert "this.gateway.post('/v1/tasks'" in client
    assert "this.gateway.get(`/v1/tasks/${taskId}`)" in client
    assert "controlUrl" not in ui_config


def test_bridge_manifests_and_packages_are_safe_local_inputs() -> None:
    manifest = json.loads((CANONICAL_ROOT / "manifests" / "omertaos-wsl.mcp.json").read_text(encoding="utf-8"))
    server_package = json.loads((CANONICAL_ROOT / "bridge-server" / "package.json").read_text(encoding="utf-8"))
    ui_package = json.loads((CANONICAL_ROOT / "bridge-ui" / "package.json").read_text(encoding="utf-8"))
    logger = (CANONICAL_ROOT / "bridge-server" / "src" / "logger.ts").read_text(encoding="utf-8")

    command = manifest["server"]["mcp_config"]["command"]
    args = " ".join(manifest["server"]["mcp_config"]["args"])
    assert command.endswith("wsl.exe")
    assert "integrations/windows-agentic-bridge/bridge-server" in args
    assert "token" not in args.lower()
    assert server_package["private"] is True
    assert ui_package["private"] is True
    assert "@modelcontextprotocol/sdk" in server_package["dependencies"]
    assert "@microsoft/ai-mcp-sdk" not in server_package["dependencies"]
    assert "ajv" in server_package["dependencies"]
    assert "@vitejs/plugin-react" in ui_package["devDependencies"]
    assert "console.log" not in logger
