# Control configuration persistence

**Document role:** migration and rollback record for the additive Control configuration state.

## Change

The Control service owns a new `control_configuration` table with a single durable row containing:

- the effective router configuration;
- an optional pending proposal;
- the previous effective configuration for one-step revert;
- the last update timestamp.

The table does not contain provider credentials or other secrets. The accepted payload is limited to routing mode, local provider name, and API provider name.

## Apply and verify

```bash
python -m control.app.network.migrate
python -m control.app.network.migrate --check
```

The migration uses SQLAlchemy `create_all` and is additive and idempotent. Existing tables and records are not changed or deleted.

## Rollback

Reverting the application code stops using the table. Leave the additive table in place so rollback is non-destructive and configuration evidence remains available. Table or row deletion requires a separate approved data migration.

