FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json tsconfig.json .eslintrc.cjs ./
COPY src ./src
RUN npm install -g pnpm && pnpm install
RUN pnpm build

FROM node:20-alpine AS runner
WORKDIR /app
COPY --from=deps /app/dist ./dist
COPY package.json ./
RUN npm install -g pnpm && pnpm install --prod
ENV NODE_ENV=production
CMD ["node", "dist/index.js"]
