---
name: deployment
description: Implement or validate OMERTAOS deployment, environment, Docker/Compose, native setup, backup, rollback, and release-readiness work. Never deploy or start persistent services unless explicitly requested.
---

# OMERTAOS Deployment Skill

## Execution Mode

- A request to implement or fix deployment assets requires configuration/script
  changes plus static or targeted validation, not a checklist-only response.
- Run read-only/configuration checks by default.
- Do not start or stop stacks/services, install OS packages, change production,
  or run a deployment unless the user explicitly requests that external-state
  action.

## Checklist

- Runtime versions and environment variables
- Docker Compose and Dockerfile contracts
- Data-service availability assumptions
- Gateway, Control, Console, and Runtime health contracts
- Secret handling and non-root execution
- Logs, backup, rollback, and platform limitations

## Quickstart Validation Order

1. `docker compose -f docker-compose.quickstart.yml config`
2. Build only when relevant to the requested change.
3. Start/use a stack and run health probes only when explicitly requested.

Never claim skipped Linux, Docker-daemon, systemd, or live-health checks passed.
