# Claude Code marketplace settings

This folder stores project-level defaults for Claude Code. The settings here tell Claude to trust and load plugins from the wshobson/agents marketplace so team members can quickly enable a curated toolset.

## Trusting this folder

Claude Code only reads settings from trusted directories. When prompted by Claude, trust the repository root of OMERTAOS so these defaults are applied. You can also trust the folder manually from the Claude interface.

## Managing plugins

Enabled plugins live under `enabledPlugins` in `settings.json` using the `plugin@marketplace`: `true` format. Toggle a plugin by setting the value to `false` or remove the entry. Add new plugins by appending new keys to the object.

## Marketplace registration

The `extraKnownMarketplaces` field registers the GitHub marketplace repository `wshobson/agents`. Claude will use this reference when resolving plugin IDs in `enabledPlugins`.

## System-managed settings

System-level overrides should be placed in `/etc/claude-code/managed-settings.json`. Use that path for fleet-wide defaults or locked settings. Project-specific preferences belong in this `.claude` directory so they stay versioned with the repo.
