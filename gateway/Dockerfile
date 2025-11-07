FROM node:20-alpine AS build
WORKDIR /app
# فقط فایلهای مربوط به گیتوی را کپی کن
COPY gateway/package*.json ./
RUN npm install
COPY gateway/ ./
# مطمئن شو tsconfig در همین /app است
RUN test -f tsconfig.json || (echo "tsconfig.json missing in /app" && ls -la && exit 1)
# اگر بیلد داری اجرا کن اگر نداری رد شو
RUN npm run build || true

FROM node:20-alpine
WORKDIR /app
ENV NODE_ENV=production
# خروجیهای ضروری را منتقل کن
COPY --from=build /app/package*.json ./
COPY --from=build /app/node_modules ./node_modules
# اگر بیلد TypeScript انجام شده:
COPY --from=build /app/dist ./dist
# برای اطمینان سورس و tsconfig هم کپی شوند (اگر start به src وابسته است)
COPY --from=build /app/src ./src
COPY --from=build /app/tsconfig.json ./tsconfig.json

EXPOSE 8080
# اگر اسکریپت start داری همین خوبه در غیر اینصورت میشه: ["node","dist/server.js"]
CMD ["npm","run","start"]
