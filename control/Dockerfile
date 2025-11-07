FROM node:20-alpine AS deps
WORKDIR /app
COPY console/package*.json ./
RUN npm install
COPY console/ ./
# اگر پروژه Next.js/React داری بیلد را تلاش کن ولی اجباری نباشد
RUN npm run build || true

FROM node:20-alpine
WORKDIR /app
ENV NODE_ENV=production
COPY --from=deps /app ./
EXPOSE 3000
# اگر next هست: ["npm","run","start"] اگر dev میخوای: ["npm","run","dev"]
CMD ["npm","run","start"]
