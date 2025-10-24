# Security Posture

- **Authentication:** NextAuth with credential hashing via Argon2 + Google OAuth.
- **Authorization:** Role-based access enforced in REST + tRPC routes.
- **Sessions:** JWT strategy with 7 day expiry; tokens include role claim.
- **Rate limiting:** Redis-backed guard to mitigate brute force.
- **Secrets management:** `.env.example` documents required environment keys.
- **Transport:** Deploy behind HTTPS reverse proxy (see runbook).
