# Claude Code marketplace integration for OMERTAOS

> Runtime alignment: Python control-plane delegates OS-level execution/isolation/sandbox to Rust `runtime-daemon` over gRPC (`shared/proto/runtime.proto`).


This guide adds first-class support for Claude Code and the wshobson/agents plugin marketplace on Debian-based hosts.

## Prerequisites

- Debian-based environment with `bash` and `curl` available
- Access to this repository
- Terminal with permissions to install user-level binaries

## Installation

Use the provided Make targets or run the scripts directly:

```bash
make claude-install           # installs Claude Code via the official installer
make claude-bootstrap         # creates .claude/settings.json with marketplace defaults
```

Dry run the installer without making changes:

```bash
scripts/claude/install-claude-code.sh --dry-run
```

## Bootstrap marketplace settings

The repo ships with `.claude/settings.json` that registers the `wshobson/agents` marketplace and enables a curated plugin set. Recreate the file or validate it anytime:

```bash
make claude-bootstrap
```

If the file is missing, the script recreates it; if present, it is validated for JSON syntax. System-wide overrides belong in `/etc/claude-code/managed-settings.json`.

## Claude commands (run inside Claude)

```text
/plugin marketplace add wshobson/agents
/plugin install python-development@wshobson/agents
/plugin install javascript-typescript@wshobson/agents
/plugin install backend-development@wshobson/agents
/plugin install kubernetes-operations@wshobson/agents
/plugin install cloud-infrastructure@wshobson/agents
/plugin install security-scanning@wshobson/agents
/plugin install code-review-ai@wshobson/agents
/plugin install full-stack-orchestration@wshobson/agents
```

## Verification

- Terminal: `make claude-status` (checks binary, version, and JSON validity)
- Console UI: open `/tools/claude` to view status, commands, and copy-ready plugin installs
- API: `GET /api/claude/status` (Console) or `GET /api/claude/recommended` (Gateway)

## Troubleshooting

- **`claude: command not found`**: Re-run `make claude-install` and ensure the install prefix (often `~/.local/bin`) is on `PATH`.
- **Interactive login required**: Launch `claude` once in a terminal to complete authentication before installing plugins.
- **Proxy or network issues**: Confirm `curl` can reach `https://claude.ai`. Respect corporate proxy settings via `http_proxy`/`https_proxy`.
- **Invalid JSON in settings**: Run `make claude-bootstrap` or validate manually with `python -m json.tool .claude/settings.json`.

## Systemd (optional)

A disabled oneshot unit is available at `deploy/systemd/omerta-claude-bootstrap.service`:

```bash
sudo systemctl enable --now omerta-claude-bootstrap.service
```

It invokes the bootstrap script to ensure marketplace settings exist. Leave it disabled unless you want automatic enforcement at boot.
