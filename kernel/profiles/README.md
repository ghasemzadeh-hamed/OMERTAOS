# Kernel Profiles

This directory stores kernel profile definitions.

## Status

`kernel/profiles` is currently **in migration** and considered incomplete.

## Minimum required profile set

- `enterprise/` (existing)
- `professional/` (scaffolded)
- `user/` (scaffolded)

## Ownership

- Runtime semantics: `kernel/*`
- Deployment overlays: `deploy/*`
- Shared config templates: `config/profiles/*`

## Rule

Do not add new profile definitions in ad-hoc top-level directories. Add them here and reference from deployment/config layers.
