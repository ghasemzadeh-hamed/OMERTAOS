FROM node:20-alpine AS deps
WORKDIR /app
COPY gateway/package*.json ./
RUN npm ci

FROM node:20-alpine AS build
WORKDIR /app
COPY gateway/tsconfig.json ./tsconfig.json
COPY gateway/src ./src
COPY --from=deps /app/node_modules ./node_modules
COPY gateway/package*.json ./
RUN npm run build

FROM node:20-alpine
WORKDIR /app
ENV NODE_ENV=production
COPY gateway/package*.json ./
RUN npm ci --omit=dev
COPY --from=build /app/dist ./dist

EXPOSE 8080
CMD ["npm", "run", "start"]
