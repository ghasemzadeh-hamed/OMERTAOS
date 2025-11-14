FROM node:20-alpine AS deps
WORKDIR /app

# Avoid running Prisma generate while prisma/schema.prisma is not yet copied
ENV SKIP_PRISMA_GENERATE=true

# Install dependencies with postinstall hook present but effectively skipped
COPY console/package*.json ./
COPY console/scripts ./scripts

RUN npm ci --ignore-scripts

# -----------------------------------------------------------------------------

FROM node:20-alpine AS build
WORKDIR /app

# Reuse installed dependencies from deps stage
COPY --from=deps /app/node_modules ./node_modules

# App sources
COPY console/package*.json ./
COPY console/next.config.mjs ./next.config.mjs
COPY console/prisma ./prisma
COPY console/scripts ./scripts
COPY console/public ./public
COPY console/src ./src

# Now prisma schema is present, run prisma generate properly
ENV SKIP_PRISMA_GENERATE=false
RUN npm run prisma:generate

# Build Next.js app
RUN npm run build

# -----------------------------------------------------------------------------

FROM node:20-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production

# Use production-ready build and deps from build stage
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/.next ./.next
COPY console/package*.json ./
COPY console/next.config.mjs ./next.config.mjs
COPY console/public ./public

EXPOSE 3000
CMD ["npm", "run", "start"]
