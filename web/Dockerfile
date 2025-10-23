FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json tsconfig.json tailwind.config.ts postcss.config.js next.config.mjs vitest.config.ts ./
COPY next-env.d.ts ./
COPY app ./app
COPY components ./components
COPY lib ./lib
COPY locales ./locales
COPY prisma ./prisma
COPY state ./state
RUN npm install -g pnpm && pnpm install
RUN pnpm build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=deps /app/.next ./.next
COPY --from=deps /app/package.json ./package.json
COPY --from=deps /app/public ./public
COPY --from=deps /app/prisma ./prisma
RUN npm install -g pnpm && pnpm install --prod
EXPOSE 3000
CMD ["pnpm", "start"]
