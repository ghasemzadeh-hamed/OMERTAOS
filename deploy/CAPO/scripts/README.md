# CAPO scripts

Phase 3 provides `install-os-packages.sh` and `install-data-services.sh` with
`--help`, `--dry-run`, platform checks, and repeatable validation. Application
and lifecycle scripts are added in phases 4-6. Every script follows the safety
and idempotency contract in the parent README. Linux-native commands must not be
executed on the Windows automation host.
