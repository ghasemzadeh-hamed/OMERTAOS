# CAPO validation, troubleshooting, and recovery

Phase 6 validates the Native and Docker Quickstart paths without treating one
as proof of the other. No legacy path may be retired until both acceptance
columns are complete and reviewed by a human.

## Validation sequence

From the repository root, validate configuration and static contracts first:

```powershell
docker compose -f docker-compose.quickstart.yml config --quiet
powershell -NoProfile -File deploy/CAPO/tests/contract-tests.ps1
python -m pytest tests/architecture -q
```

On the intended Debian/Ubuntu SSD host, run the read-only Native probe after
first boot:

```bash
bash deploy/CAPO/scripts/smoke-test.sh --mode native
```

For a running Quickstart stack, run:

```bash
bash deploy/CAPO/scripts/smoke-test.sh --mode quickstart
```

The probes require HTTP success from Control `8000`, Gateway `8080`, and
Console `3000`. Native also requires the Runtime unit and aggregate target to
be active. Quickstart requires its Runtime container to be running; the
Compose healthcheck remains the authoritative gRPC readiness probe on `50051`.

## Troubleshooting

- Control failure: check PostgreSQL and Redis readiness, then inspect
  `journalctl -u omertaos-control.service` or Quickstart Control logs. Do not
  replace missing required stores with memory-only state.
- Gateway failure: verify Control health and `AION_CONTROL_BASE_URL`; Gateway
  must route to Control rather than bypass it.
- Console failure: distinguish browser `NEXT_PUBLIC_GATEWAY_URL` from the
  server-side Gateway address and confirm port `3000` is free.
- Runtime failure: inspect the Runtime unit/container and bind address
  `127.0.0.1:50051` (Native) or `0.0.0.0:50051` inside Quickstart. Do not add
  unsupported runtime flags.
- Optional MongoDB, Qdrant, or MinIO failure: keep its `CAPO_*_ENABLED` flag
  false until the endpoint and credentials are validated. The capability must
  remain explicitly degraded without weakening authorization.

## Non-destructive rollback

Preview and then execute Native lifecycle rollback:

```bash
bash deploy/CAPO/scripts/rollback.sh --dry-run
bash deploy/CAPO/scripts/rollback.sh
```

This stops and disables only `omertaos.target`. It deliberately preserves the
repository, `/etc/omertaos/omertaos.env`, `/var/lib/omertaos`, service account,
PostgreSQL roles/databases, Redis state, and all legacy recovery inputs. Revert
the phase commit separately if the deployment assets themselves must be
removed from a future checkout.

Quickstart rollback is `docker compose -f docker-compose.quickstart.yml down`
without `--volumes`; named volumes and data remain intact.

## Acceptance state

Static validation on Windows can confirm syntax, contracts, Compose rendering,
and application tests. It cannot prove native systemd, ownership, package, or
SSD behavior. Those Native checks remain pending until recorded from the real
Linux host. A full running Quickstart smoke is also recorded independently;
configuration rendering alone is not runtime acceptance.
