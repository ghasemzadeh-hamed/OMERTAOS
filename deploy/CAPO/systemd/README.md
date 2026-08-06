# CAPO systemd compatibility payload

These six files mirror the canonical assets in `deploy/native/systemd` for CAPO
compatibility. The CAPO setup and lifecycle entrypoints are thin wrappers around
the Native N6 scripts. Changes must be made in the Native owner first and the
contract tests require byte-for-byte parity.

The stack order is PostgreSQL/Redis, the N5 one-shot install unit, Runtime,
Control, Gateway, and Console. Services remain stopped after setup; Native Linux
and live systemd verification remain N7 acceptance work.

N8 application paths resolve through `/opt/omertaos/current`; version switching
is owned by the canonical Native update and rollback scripts.
