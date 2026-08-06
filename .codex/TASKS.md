# OMERTAOS CAPO Task Board

> Historical reference only. All seven CAPO phases were recorded complete in
> `deploy/CAPO/PHASE_STATUS.md`. This file is not an active Codex task queue and
> must never override the current user request, checked-out branch, or current
> canonical migration contract.

## Historical Focus

- [ ] Switch or create branch capo.
- [ ] Run Doctor action.
- [ ] Run Native Setup action.
- [ ] Validate Python dependency setup.
- [ ] Validate console npm install.
- [ ] Validate gateway npm install.
- [ ] Validate Docker Compose config.
- [ ] Fix missing control/Dockerfile if needed.
- [ ] Fix missing gateway/Dockerfile if needed.
- [ ] Add or verify control health endpoints.
- [ ] Add or verify gateway health endpoint.
- [ ] Ensure kernel references do not break quickstart.

## Quickstart Stabilization

- [ ] Inspect docker-compose.quickstart.yml.
- [ ] Inspect docker-compose.local.yml.
- [ ] Inspect .env.example, .env.schema, dev.env.
- [ ] Inspect quick-install.sh and quick-install.ps1.
- [ ] Ensure Console uses port 3000.
- [ ] Ensure Gateway uses port 8080.
- [ ] Ensure Control uses port 8000.
- [ ] Keep Runtime gRPC 50051 optional in this phase.

## AION Roadmap Backlog

- [ ] Agent Registry.
- [ ] Task Registry.
- [ ] Workflow Engine.
- [ ] Gateway Task API.
- [ ] Runtime Execution.
- [ ] Audit Log.
- [ ] RAG ingestion and retrieval.
- [ ] Model / Prompt Registry.
- [ ] Policy Manager.
- [ ] Prompt Firewall.
- [ ] Tenant Isolation.
- [ ] Human Approval.
- [ ] Automation Builder.

## Do Not Touch Without Approval

- Authentication flow
- Runtime execution boundary
- Production database migrations
- Permission system
- Secret store
- Existing schemas/protobuf contracts
- Docker compose service topology
- Legacy compatibility folders
- Windows Agentic Bridge
