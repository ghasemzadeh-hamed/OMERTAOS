"""CLI helper for managing AION packages."""
from __future__ import annotations

import argparse

from os.control.os.api import packages as api_packages


def cmd_list(_: argparse.Namespace) -> int:
    registry = api_packages._load_registry()
    state = api_packages._load_state()
    installed = {pkg["name"] for pkg in state.get("installed", [])}
    for entry in registry:
        mark = "*" if entry.get("name") in installed else "-"
        version = entry.get("version", "")
        print(f"{mark} {entry.get('name')} {version}")
    return 0


def cmd_install(args: argparse.Namespace) -> int:
    registry = {entry.get("name"): entry for entry in api_packages._load_registry()}
    if args.name not in registry:
        raise SystemExit(f"Package {args.name} not found in registry")
    state = api_packages._load_state()
    installed = [pkg for pkg in state.get("installed", []) if pkg.get("name") != args.name]
    installed.append({"name": args.name, "installed_at": registry[args.name].get("version", "unknown")})
    state["installed"] = installed
    api_packages._write_state(state)
    print(f"Installed {args.name}")
    return 0


def cmd_remove(args: argparse.Namespace) -> int:
    state = api_packages._load_state()
    state["installed"] = [pkg for pkg in state.get("installed", []) if pkg.get("name") != args.name]
    api_packages._write_state(state)
    print(f"Removed {args.name}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AION package manager")
    sub = parser.add_subparsers(dest="command", required=True)

    sub_list = sub.add_parser("list", help="List packages")
    sub_list.set_defaults(func=cmd_list)

    sub_install = sub.add_parser("install", help="Install a package")
    sub_install.add_argument("name")
    sub_install.set_defaults(func=cmd_install)

    sub_remove = sub.add_parser("remove", help="Remove a package")
    sub_remove.add_argument("name")
    sub_remove.set_defaults(func=cmd_remove)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
