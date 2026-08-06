# OMERTAOS Codex Package Changelog

## Unreleased

- Added a root-scoped, action-first `AGENTS.md` so implementation requests lead
  to patches and validation instead of documentation-only output.
- Added trusted-project Codex defaults with medium reasoning, low response
  verbosity, workspace-write sandboxing, and on-request escalation.
- Marked CAPO task/context snapshots as non-authoritative and removed the fixed
  branch assumption from active guidance.
- Clarified conditional documentation and the distinction between OMERTAOS
  runtime-agent policy and Codex engineering permissions.
- Prepared repository skills for discovery from `.agents/skills` and hardened
  local test/lint wrappers to propagate failures.
- Added OMERTAOS-specific Codex/Agent environment.
- Added CAPO Native-first setup rules.
- Added do-not-delete protection rules.
- Added Docker quickstart validation actions.
- Added AION architecture context.
