# Runbook

## 1. Bootstrapping
1. Copy `.env.example` to `.env` and fill secrets.
2. Run `docker compose up --build` to start web, Postgres, Redis.
3. Execute `pnpm prisma migrate deploy` and `pnpm prisma db seed` (inside container) to initialize data.

## 2. Operations
- **Health check:** `GET /api/rest/tasks` returns 200 for authenticated users.
- **Cache purge:** Restart Redis container (`docker compose restart redis`).
- **Reset admin password:** Run Prisma script `pnpm ts-node prisma/seed.ts` with new hash.
- **Scale:** Increase `web` replicas via Compose or deploy to Kubernetes using same Docker image.

## 3. Incident Response
- **Auth failure spikes:** Inspect Redis keys `ratelimit:*` and NextAuth logs; temporarily raise limits with env vars.
- **DB migration rollback:** `pnpm prisma migrate resolve --rolled-back <migration>` then redeploy.
- **Real-time outage:** Ensure webhook posts are received; check logs for `publishTaskUpdate`.

## 4. Deployment
- CI pipeline builds image and runs tests. On success, push container to registry and run migrations before swapping traffic.
- Set `NEXTAUTH_URL` to production domain and configure Google OAuth callback.
