from __future__ import annotations

import argparse
import subprocess
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts" / "claude"

RECOMMENDED_PLUGINS = [
    "python-development@wshobson/agents",
    "javascript-typescript@wshobson/agents",
    "backend-development@wshobson/agents",
    "kubernetes-operations@wshobson/agents",
    "cloud-infrastructure@wshobson/agents",
    "security-scanning@wshobson/agents",
    "code-review-ai@wshobson/agents",
    "full-stack-orchestration@wshobson/agents",
]


def _run_script(script_name: str, args: Iterable[str] | None = None) -> int:
    script_path = SCRIPTS_DIR / script_name
    if not script_path.exists():
        print(f"Script not found: {script_path}")
        return 1

    cmd = [str(script_path)]
    if args:
        cmd.extend(args)

    result = subprocess.run(cmd, check=False)
    return result.returncode


def _print_plugin_instructions() -> None:
    print("Marketplace: wshobson/agents")
    print("Recommended plugins:")
    for plugin in RECOMMENDED_PLUGINS:
        print(f"  - {plugin}")
    print("Commands to run inside Claude:")
    print("  /plugin marketplace add wshobson/agents")
    for plugin in RECOMMENDED_PLUGINS:
        print(f"  /plugin install {plugin}")


def register(parser: argparse.ArgumentParser) -> None:
    subparsers = parser.add_subparsers(dest="claude_command", required=True)

    install_parser = subparsers.add_parser("install", help="Install Claude Code on Debian hosts")
    install_parser.add_argument("--dry-run", action="store_true", help="Print actions without running them")

    bootstrap_parser = subparsers.add_parser("bootstrap", help="Ensure marketplace config exists")
    bootstrap_parser.add_argument(
        "--install-plugins",
        action="store_true",
        help="Attempt non-interactive plugin install when supported",
    )

    status_parser = subparsers.add_parser("status", help="Check Claude installation state")
    status_parser.add_argument("--json", action="store_true", help="Emit JSON for automation")

    subparsers.add_parser("plugins", help="List recommended marketplace plugins")

    open_parser = subparsers.add_parser("open", help="Show how to open the Claude TUI")
    open_parser.add_argument(
        "--execute",
        action="store_true",
        help="Launch 'claude' directly. Leave unset to only print the command.",
    )


def handle(args: argparse.Namespace) -> int:
    command = args.claude_command

    if command == "install":
        extra = ["--dry-run"] if getattr(args, "dry_run", False) else []
        return _run_script("install-claude-code.sh", extra)

    if command == "bootstrap":
        extra = ["--install-plugins"] if getattr(args, "install_plugins", False) else []
        return _run_script("bootstrap-marketplace.sh", extra)

    if command == "status":
        extra = ["--json"] if getattr(args, "json", False) else []
        return _run_script("status.sh", extra)

    if command == "plugins":
        _print_plugin_instructions()
        return 0

    if command == "open":
        if getattr(args, "execute", False):
            return subprocess.run(["claude"], check=False).returncode
        print("Run 'claude' from a trusted terminal session to launch Claude Code.")
        print("If it is not on PATH, re-run the installer or add the install prefix to PATH.")
        return 0

    print(f"Unknown claude subcommand: {command}")
    return 1
