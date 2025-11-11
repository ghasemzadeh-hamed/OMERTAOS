FROM node:20-bullseye-slim AS build

WORKDIR /app

COPY gateway/package.json gateway/package-lock.json ./gateway/
COPY shared/secret-provider-node ./shared/secret-provider-node

RUN cd gateway && npm ci

COPY gateway ./gateway

RUN cd gateway && npm run build && npm prune --omit=dev

FROM node:20-bullseye-slim

WORKDIR /app

ENV NODE_ENV=production

COPY --from=build /app/gateway/dist ./dist
COPY --from=build /app/gateway/node_modules ./node_modules
COPY --from=build /app/gateway/package.json ./package.json

CMD ["node", "dist/server.js"]
