---
name: refactor
description: Implement a user-requested OMERTAOS refactor while preserving behavior, compatibility paths, and canonical ownership. Do not trigger for planning-only or unrelated implementation work.
---

# OMERTAOS Refactor Skill

## Execution Mode

- Refactor only the scope named by the user or the explicitly invoked migration
  phase.
- Inspect references and tests, apply the focused refactor, then validate it in
  the same task. Do not substitute a migration-plan Markdown file.
- A historical roadmap is context, not authorization for the next phase.

## Rules

- Preserve behavior and public interfaces.
- Do not rewrite the system or delete compatibility folders.
- Use small, testable changes and avoid unnecessary dependencies.
- Before moving anything, inspect imports/references and Git history with focused
  `rg` and `git log -- <path>` commands.

## Canonical Ownership Reference

Use `docs/adr/0001-canonical-aion-ownership.md` and
`docs/migration/canonical-paths.md`. Verify current repository state before
acting; never infer that a listed compatibility path may be deleted.
