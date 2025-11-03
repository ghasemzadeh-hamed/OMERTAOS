"""Command line interface entrypoint for AION-OS."""
from __future__ import annotations

import argparse
from typing import Callable, Dict

from . import install, status, policy, personal, backup

COMMANDS: Dict[str, Callable[[argparse.Namespace], int]] = {
    "install": install.handle,
    "status": status.handle,
    "policy": policy.handle,
    "personal": personal.handle,
    "backup": backup.handle,
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AION-OS command line interface")
    subparsers = parser.add_subparsers(dest="command", required=True)

    install.register(subparsers.add_parser("install", help="Install runtime services"))
    status.register(subparsers.add_parser("status", help="Inspect runtime health"))
    policy.register(subparsers.add_parser("policy", help="Manage policy packages"))
    personal.register(subparsers.add_parser("personal", help="Personal edition helpers"))
    backup.register(subparsers.add_parser("backup", help="Backup and restore"))
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    handler = COMMANDS.get(args.command)
    if not handler:
        parser.error(f"unknown command {args.command}")
    return handler(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
