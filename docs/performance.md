# Performance Notes

- **Caching:** Redis used for rate limiting; extendable for query caching.
- **Prisma indexes:** Unique indexes on user email and session tokens reduce query time.
- **Code splitting:** App Router automatically chunks; heavy widgets lazy-load via suspense fallback.
- **Static assets:** Next.js image optimization ready via remote patterns.
- **CI budget:** `pnpm build` ensures tree-shaking and type-safe bundling.
