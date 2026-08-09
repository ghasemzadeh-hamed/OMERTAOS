# OMERTAOS Console

The Console is the Next.js 14 presentation layer for operator workflows. It may
call the Gateway public API; it must not address Control, Runtime, or data stores
directly.

**Status:** implemented prototype. Unit and end-to-end test sources exist, but a
production build does not by itself validate live authentication, streaming,
RTL, or full-stack behavior.

## Canonical endpoints

The Quickstart Compose model uses:

| Setting | Value |
|---|---|
| Console origin | `http://localhost:3000` |
| Browser-visible Gateway | `http://localhost:8080` |
| Container-visible Gateway | `http://gateway:8080` |

Set `NEXT_PUBLIC_GATEWAY_URL=http://localhost:8080` for browser requests and
`GATEWAY_URL=http://gateway:8080` inside Compose. Some source-level fallback
values are retained for compatibility; do not rely on them as canonical
configuration.

## Local development

```bash
corepack enable
pnpm install --frozen-lockfile
pnpm dev
```

From the repository root, the supported service model is:

```bash
docker compose --project-directory . -f deploy/docker/compose/quickstart.yml config
docker compose --project-directory . -f deploy/docker/compose/quickstart.yml up --build console
```

Starting services changes local container state. Review environment values and
replace all development secrets first.

## Required configuration

| Variable | Purpose |
|---|---|
| `NEXTAUTH_URL` | Public Console origin, normally `http://localhost:3000` |
| `NEXTAUTH_SECRET` | Secret used to sign authentication state |
| `NEXT_PUBLIC_GATEWAY_URL` | Gateway origin visible to the browser |
| `GATEWAY_URL` / `AION_GATEWAY_URL` | Gateway origin used by server routes |
| `DATABASE_URL` | Prisma database used by setup and credential authentication |

Never use the example `NEXTAUTH_SECRET`, admin password, or development token
in a public environment.

## Authentication and setup

The current NextAuth configuration uses a credential provider backed by Prisma
users and bcrypt password verification. Sessions use signed JWT state and carry
the stored role. The setup workflow persists completion state and the
middleware redirects incomplete installations to `/setup`.

Google OAuth is not configured in the current `console/lib/auth.ts`; adding it
would require a separate reviewed authentication change and updated tests.

## Health and architecture

`/api/system/health` checks Console and Gateway. Control health is read from
Gateway dependency information so the presentation layer does not create a
direct Control path.

Manual development checks:

```bash
curl http://localhost:3000/healthz
curl http://localhost:8080/health
```

Interpret each response according to the implementation; availability does not
prove authentication, policy, persistence, or Runtime acceptance.

## Commands

| Command | Purpose |
|---|---|
| `pnpm dev` | Development server |
| `pnpm build` | Production compilation |
| `pnpm start` | Serve a production build |
| `pnpm test -- --config vitest.config.mts` | Vitest suite |
| `pnpm playwright:test` | Playwright scenarios |
| `pnpm prisma:generate` | Generate the Prisma client |

The interface includes English/Persian message resources and RTL-oriented test
coverage. Claims about accessibility, browser compatibility, and live
multi-service behavior require an executed browser test record.
