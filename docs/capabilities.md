# Capabilities Index (UI + Docs Source of Truth)

This document maps the platform capabilities to their backend APIs, configuration, and UI surface. It is backed by [`config/capabilities.yaml`](../config/capabilities.yaml) as the single source of truth for Console and documentation alignment.

## Architecture at a Glance

- **Kernel + Registry**: Rust kernels in `kernel/` and `kernel-multitenant/` schedule tasks/agents for single- and multi-tenant modes.
- **Control Plane (Python)**: Services in `aion/`, `os/control/`, and `aionos_control/` manage state, policy, memory, task routing, and persist canonical profile data.
- **Gateway (TypeScript/Fastify)**: API/Auth/Model proxy between Console and runtime backends. Exposes config/model/agent lifecycle routes and supports admin JWT/API key enforcement.
- **Console (Next.js / Glass)**: UI that delivers setup wizard, onboarding, dashboards, agent catalog/my-agents, auth flows, and configuration tooling.
- **AI Registry & Models**: `ai_registry/REGISTRY.yaml` and manifests under `models/` provide versioning and audit trail for models.
- **Agents/Policies/Catalog Schemas**: Definitions in `agents/`, `policies/`, and `config/agent_catalog/` map directly to Console wizards and catalog templates.

## Capability Overview

Each capability below is defined in the YAML registry and consumed by UI flows and docs.

### Setup & Profiles
- **APIs**: GET/POST `/v1/config/profile` (Gateway), `/api/setup/profile` (Console proxy).
- **State**: Control persists `.aionos/profile.json`; `setupDone` flag drives routing.
- **Config**: `AION_ENV`, `AION_PROFILE`, `TENANCY_MODE`.
- **UI**: `/setup` wizard with profile selection and completion redirect.
- **RBAC/Tenancy**: Dev bootstrap can bypass JWT; supports single- and multi-tenant.

### Auth & RBAC
- **APIs**: JWT/API Key enforcement across Gateway; Console session via `/login` with middleware redirects for setup/onboarding.
- **Config**: `AION_GATEWAY_ADMIN_TOKEN`, `AION_GATEWAY_API_KEYS`, `AION_JWT_PUBLIC_KEY`, `AION_JWT_SECRET_PATH`, `NEXTAUTH_SECRET`, `NEXTAUTH_URL`, `NEXT_PUBLIC_GATEWAY_URL`.
- **UI**: Login screen, session state, admin role required for config routes; tenant header support.

### Onboarding Gate
- **Behavior**: Middleware sends users to `/onboarding` until `onboardingComplete` is true.
- **UI**: Onboarding checklist/flow.

### Agent Catalog
- **APIs**: GET `/api/agent-catalog` (Gateway), tenant-aware via `tenant-id` header.
- **UI**: `/agents/catalog` list with category filter, capabilities/tags/icons, and CTA to configure/deploy from recipe/schema.

### My Agents
- **APIs**: GET `/api/agents`, POST `/api/agents/{id}/deploy`, POST `/api/agents/{id}/disable`.
- **UI**: `/agents/my-agents` table/list showing status/enabled/scope/updated_at with deploy/disable actions and optimistic refresh.

### Configuration Lifecycle (Admin)
- **APIs**: POST `/v1/config/propose`, POST `/v1/config/apply`, POST `/v1/config/revert`, GET `/v1/config/status` (admin-only).
- **UI**: Configuration page exposing propose/apply/revert/status actions with audit/status display.
- **Auth**: Requires admin role via Gateway.

### Models Registry
- **APIs**: GET `/v1/models` (includes provider/profile, falls back gracefully on errors).
- **UI**: Models list with provider/profile/status.

### LatentBox Tool Discovery (Feature-Flagged)
- **Flag**: `FEATURE_LATENTBOX_RECOMMENDATIONS` controls visibility.
- **Data**: `config/latentbox/tools.yaml` supplies tool metadata.
- **UI**: Tool discovery/search/sync section shown only when flag is enabled.

## Config Map (Env & Feature Flags)

Treat `dev.env` as the current development reference and surface these variables in UI/Docs when relevant:

- **Core/Shared**: `AION_ENV`, `AION_PROFILE`, `TENANCY_MODE`, `FEATURE_LATENTBOX_RECOMMENDATIONS`.
- **Database/Storage/Infra**: `AION_DB_USER`, `AION_DB_PASSWORD`, `AION_DB_NAME`, `DATABASE_URL`, `AION_CONTROL_POSTGRES_DSN`, `AION_CONTROL_REDIS_URL`, `AION_REDIS_URL`, `AION_CONTROL_MONGO_DSN`, `AION_CONTROL_QDRANT_URL`, `AION_CONTROL_MINIO_ENDPOINT`, `AION_CONTROL_MINIO_ACCESS_KEY`, `AION_CONTROL_MINIO_SECRET_KEY`, `AION_CONTROL_MINIO_BUCKET`, `AION_CONTROL_MINIO_SECURE`.
- **Gateway/Auth**: `AION_GATEWAY_ADMIN_TOKEN`, `AION_GATEWAY_API_KEYS`, `AION_JWT_PUBLIC_KEY`, `AION_JWT_SECRET_PATH` (plus related secret-path variants).
- **Console**: `NEXTAUTH_SECRET`, `NEXTAUTH_URL`, `NEXT_PUBLIC_GATEWAY_URL`, `CONSOLE_ADMIN_EMAIL`, `CONSOLE_ADMIN_PASSWORD`, `SKIP_CONSOLE_SEED`.
- **Telemetry/TLS**: `AION_TLS_REQUIRED`, `AION_TLS_REQUIRE_MTLS`, `AION_TELEMETRY_OPT_IN`, `AION_TELEMETRY_ENDPOINT`.

## Deployment Mode Reference

Use these compose variants to align UI messaging with runtime expectations:
- `docker-compose.yml`: Baseline stack with control, gateway, console, Postgres, Redis, Qdrant, MinIO, optional Vault, and dev kernel profile.
- `docker-compose.quickstart.yml`: Fast path using `.env`, Gateway on 8080, Console on 3000, `AION_AUTH_MODE=disabled` for bootstrap.
- `docker-compose.local.yml`: Local-friendly defaults (e.g., Vault raft, simplified secrets).

Expose the chosen mode in UI/Docs along with port/auth differences so users know what to expect in each environment.
