# مرحله ۱: Build کردن پروژه React
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# مرحله ۲: آماده‌سازی فایل‌های نهایی
FROM alpine:latest
WORKDIR /dist
COPY --from=builder /app/dist /dist
CMD ["sleep", "infinity"]