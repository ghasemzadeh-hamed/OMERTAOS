# aionOS Glass Console

The aionOS Glass Console provides an authenticated dashboard for managing tasks, policies, modules, and telemetry across the platform. The interface uses a translucent "glass" aesthetic with responsive layouts, RTL support, and real-time updates via SSE/WebSockets.

## Getting started

```bash
pnpm install
pnpm dev
```

The app expects the gateway and control plane to run locally using `docker compose up` from the project root. Copy `.env.local.example` to `.env.local` and populate OAuth secrets if you want to test Google login.

### Local run (console + gateway + control)

Required environment variables:

- `NEXT_PUBLIC_GATEWAY_URL` (defaults to `http://localhost:3000`)
- `NEXTAUTH_URL` (console origin, e.g. `http://localhost:3001`)
- `NEXTAUTH_SECRET` (32+ bytes)

Startup commands:

```bash
# from repo root
docker compose -f docker-compose.quickstart.yml up gateway control console
# or run just the console (gateway/control already running)
cd console && pnpm dev
```

Manual smoke checks:

| Scenario | Command/URL | Expected |
| --- | --- | --- |
| Health | `curl http://localhost:3001/healthz` | HTTP 200 |
| First visit (no setup) | `http://localhost:3001/` | Redirects to `/setup` |
| After setup, logged out | `http://localhost:3001/` | Redirects to `/login` |
| After login | `http://localhost:3001/` | Shows dashboard |
| Exit | `http://localhost:3001/exit` | Signs out to `/login` |

## Scripts

| Command                | Description                                |
| ---------------------- | ------------------------------------------ |
| `pnpm dev`             | Run the development server with hot reload |
| `pnpm build`           | Create a production build                  |
| `pnpm start`           | Start the production server                |
| `pnpm lint`            | Run ESLint                                 |
| `pnpm test`            | Execute Vitest unit tests                  |
| `pnpm playwright:test` | Run Playwright end-to-end tests            |

## Authentication

NextAuth handles credential and Google OAuth logins. Credentials are validated against the gateway `/v1/auth/login` endpoint, while Google uses OAuth tokens to map to existing platform users. Roles (admin, manager, user) are embedded in the session token and consumed via the `useAuth` hook.

Required environment variables:

| Variable                  | Purpose                                                                                       |
| ------------------------- | --------------------------------------------------------------------------------------------- |
| `NEXTAUTH_SECRET`         | Random 32+ byte secret used to sign session cookies. Generate with `openssl rand -base64 32`. |
| `NEXTAUTH_URL`            | Public URL where the console is served (e.g. `http://localhost:3001`).                        |
| `NEXT_PUBLIC_GATEWAY_URL` | Base URL for REST/gRPC proxies exposed by the gateway (defaults to `http://localhost:3000`).  |

### Credentials flow

Add the credential provider to `providers/credentials.ts` (already wired) and ensure the gateway exposes `/v1/auth/login`. The console will POST `{ email, password }` to the gateway and expects a JSON body with `token`, `roles`, and optional `tenant`. Set `AION_GATEWAY_BASE` accordingly in `.env.local` if you are not using Docker defaults.

### Google OAuth flow

Populate `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in `.env.local`. In the Google Cloud Console configure an OAuth consent screen and add an authorized redirect URI pointing to `${NEXTAUTH_URL}/api/auth/callback/google`. The provider automatically maps Google email addresses to existing AION users by email and reuses the RBAC roles provisioned in the control plane.

## Real-time updates

The console listens for task updates with SSE first and falls back to WebSockets. Optimistic updates leverage TanStack Query for client-side cache management.

## i18n and RTL

Use the language toggle in the navbar to switch between English and Persian (RTL). Layout direction switches automatically, and translated strings live under `messages/en.json` and `messages/fa.json`.

## Testing

Vitest covers critical UI primitives such as the glass cards, task board, and policy editor. Playwright scenarios exercise authentication, live task streaming, RTL layout, and rate-limiting feedback.

## Deployment

The console compiles to static assets with server components for authenticated routes. Include it in Docker Compose or Kubernetes by exposing port 3001 and mounting the same environment variables documented in `.env.local.example`.

## Schema-driven console and AI guardrails

The console now renders primary flows (setup, onboarding, agents, admin, and models) from JSON schemas stored in `/config`:

- `/config/capabilities.json`: backend endpoints, RBAC, feature flags, tenancy needs, and UI route metadata.
- `/config/navigation.json`: navigation groups/items mapped to capability IDs with ordering.
- `/config/pages/*.page.json`: page schemas describing layout, sections, components, data sources, and actions.

`@/lib/navigationResolver` filters navigation by user role and active feature flags while preserving critical flows such as setup, onboarding, agent catalog, and my agents. `@/lib/pageRenderer` consumes the page schema to render forms, tables, stats, and actions, calling Gateway/Control endpoints through `@/lib/endpointClient` with tenant headers when present. AI-driven suggestions are mediated by `@/lib/ai/uiOrchestrator`, which validates patches against allowlists (no secret exposure, no RBAC escalation, critical routes protected) before applying optional tweaks. To add a new page, drop a schema in `/config/pages`, register a capability in `/config/capabilities.json`, map it in `/config/navigation.json`, and create a thin route that loads the schema and passes session context (role, feature flags, tenancy).
