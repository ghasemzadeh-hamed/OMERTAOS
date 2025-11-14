# Stage 1: install dependencies with pnpm
FROM node:20-alpine AS deps

WORKDIR /workspace

# Enable pnpm via corepack so the image uses the same package manager version
RUN corepack enable && corepack prepare pnpm@latest --activate

# Copy the console manifest and the local workspace packages it depends on
COPY console/package.json console/pnpm-lock.yaml ./console/
COPY shared/secret-provider-node ./shared/secret-provider-node
COPY packages/ui-core ./packages/ui-core

WORKDIR /workspace/console

RUN pnpm install --frozen-lockfile --ignore-scripts

# Stage 2: build (Next.js + Prisma generate)
FROM node:20-alpine AS builder

WORKDIR /workspace
RUN corepack enable && corepack prepare pnpm@latest --activate

# Reuse installed dependencies from deps stage
COPY --from=deps /workspace/console/node_modules ./console/node_modules

# Copy full source and shared packages required for build-time steps
COPY console/. ./console
COPY shared/secret-provider-node ./shared/secret-provider-node
COPY packages/ui-core ./packages/ui-core

WORKDIR /workspace/console

# Ensure the public directory exists so the runtime stage can copy it even when
# the application does not ship static assets. This avoids COPY failures on CI
# when the folder is absent from the source tree.
RUN mkdir -p public

# Provide Prisma with a safe build-time DATABASE_URL so it can emit the client without
# talking to a live database. Runtime deployments still override DATABASE_URL via their
# own environment configuration (docker-compose, k8s secrets, etc.).
ARG PRISMA_DATABASE_URL="postgresql://placeholder:placeholder@localhost:5432/placeholder?schema=public"
ENV DATABASE_URL=${PRISMA_DATABASE_URL}

RUN pnpm prisma generate
RUN pnpm build
RUN pnpm prune --prod

# Stage 3: runtime image
FROM node:20-alpine AS runner

WORKDIR /app
ENV NODE_ENV=production

# Create non-root user for running the app
RUN addgroup -g 1001 -S nodejs \
  && adduser -S nextjs -u 1001

# Copy only the files required at runtime
COPY --from=builder /workspace/console/public ./public
COPY --from=builder /workspace/console/.next ./.next
COPY --from=builder /workspace/console/node_modules ./node_modules
COPY --from=builder /workspace/console/package.json ./package.json
COPY --from=builder /workspace/console/next.config.mjs ./next.config.mjs
COPY --from=builder /workspace/console/prisma ./prisma

USER nextjs

EXPOSE 3000

CMD ["node", "node_modules/next/dist/bin/next", "start", "-p", "3000"]
