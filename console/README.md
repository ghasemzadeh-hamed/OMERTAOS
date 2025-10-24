# aionOS Glass Console

The aionOS Glass Console provides an authenticated dashboard for managing tasks, policies, modules, and telemetry across the platform. The interface uses a translucent "glass" aesthetic with responsive layouts, RTL support, and real-time updates via SSE/WebSockets.

## Getting started

```bash
pnpm install
pnpm dev
```

The app expects the gateway and control plane to run locally using `docker compose up` from the project root. Copy `.env.local.example` to `.env.local` and populate OAuth secrets if you want to test Google login.

## Scripts

| Command | Description |
| --- | --- |
| `pnpm dev` | Run the development server with hot reload |
| `pnpm build` | Create a production build |
| `pnpm start` | Start the production server |
| `pnpm lint` | Run ESLint |
| `pnpm test` | Execute Vitest unit tests |
| `pnpm playwright:test` | Run Playwright end-to-end tests |

## Authentication

NextAuth handles credential and Google OAuth logins. Credentials are validated against the `AION_CONSOLE_USERS` roster (format `email:password:role1|role2[:tenant]`) that mirrors gateway roles. When Google OAuth is configured the resulting user defaults to the `user` role unless upgraded via policy. Roles (admin, manager, user) are embedded in the session token and consumed via the `useAuth` hook.

## Real-time updates

The console listens for task updates with SSE first and falls back to WebSockets. Optimistic updates leverage TanStack Query for client-side cache management.

## i18n and RTL

Use the language toggle in the navbar to switch between English and Persian (RTL). Layout direction switches automatically, and translated strings live under `messages/en.json` and `messages/fa.json`.

## Testing

Vitest covers critical UI primitives such as the glass cards, task board, and policy editor. Playwright scenarios exercise authentication, live task streaming, RTL layout, and rate-limiting feedback.

## Deployment

The console compiles to static assets with server components for authenticated routes. Include it in Docker Compose or Kubernetes by exposing port 3000 and mounting the same environment variables documented in `.env.local.example`.
