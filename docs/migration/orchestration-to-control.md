# S2.2 migration — orchestration to Control

Date: 2026-07-12

Status: canonical primitives migrated; the legacy root remains a compatibility
surface until the S5 deletion gate.

## Impact analysis

- Canonical owner: `control/orchestration/`
- Legacy input: `orchestration/dag.py` and `orchestration/scheduler.py`
- Database, API, UI and permission impact: none.
- Deployment impact: none; the Control image already copies `control/`.
- Risk: medium because scheduling order is Control decision logic, although no
  production caller currently imports the legacy prototypes.

## Behavior

The in-memory DAG and deterministic resource scheduler moved to canonical
Control ownership. Compatibility modules now re-export canonical types and
cannot diverge.

The migration preserves GPU-first, then CPU and memory ordering. A final task-ID
tie-break makes equal resource requests deterministic. Validation now rejects:

- empty node, task or tenant identifiers;
- duplicate nodes or scheduling task IDs;
- self, missing or cyclic DAG dependencies;
- non-positive CPU or memory requests.

This remains a prototype primitive. It does not claim durable workflow state,
tenant fairness, policy decisions, retries, approvals or event emission; those
features require their own later phase and persistence contracts.

## Validation

```powershell
python -m pytest tests/control/test_orchestration.py -q
python -m pytest tests/control -q
python -m pytest tests/architecture -q
docker compose -f docker-compose.quickstart.yml config --quiet
```

The Structure completion gate remains expected-red while protected legacy roots
exist. Immediate boundary checks must stay green.

## Migration and rollback

No database migration is needed. Revert the S2.2 commit as one unit to restore
the previous prototypes. Do not delete the compatibility root or persistent
state. Permanent root retirement remains an S5 operation requiring human review.
