# AION Dashboard

A production-ready Next.js + FastAPI-style backend (via Next API routes and tRPC) operations center with glassmorphism design.

## Getting Started

```bash
pnpm install
pnpm prisma migrate dev
pnpm prisma db seed
pnpm dev
```

Use `.env.example` as template.

## Testing

```bash
pnpm lint
pnpm test
pnpm test:ui
```

## Docker

```bash
docker compose up --build
```
