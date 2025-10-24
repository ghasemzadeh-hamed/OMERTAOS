FROM node:20-alpine AS base
WORKDIR /app
COPY package.json tsconfig.json .eslintrc.cjs ./
RUN npm install --legacy-peer-deps
COPY src ./src
RUN npm run build

FROM node:20-alpine
WORKDIR /app
COPY --from=base /app/node_modules ./node_modules
COPY --from=base /app/dist ./dist
COPY package.json ./
ENV NODE_ENV=production
EXPOSE 8080
CMD ["node", "dist/index.js"]
