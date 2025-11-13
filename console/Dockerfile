FROM node:20-alpine AS deps
WORKDIR /app
COPY console/package*.json ./
RUN npm ci

FROM node:20-alpine AS build
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY console/ ./
RUN npm run build

FROM node:20-alpine
WORKDIR /app
ENV NODE_ENV=production
COPY console/package*.json ./
COPY console/next.config.mjs ./next.config.mjs
# Install production dependencies without running lifecycle scripts
# (postinstall attempts to run scripts/run-prisma-generate.cjs which is not
# copied into this stage).
RUN npm ci --omit=dev --ignore-scripts
COPY --from=build /app/.next ./.next

EXPOSE 3000
CMD ["npm", "run", "start"]
