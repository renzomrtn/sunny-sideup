# ── Stage 1: Build Vue app ────────────────────────────────────
FROM node:22-alpine AS builder

WORKDIR /app

# Copy dependencies
COPY package.json package-lock.json* ./
RUN npm install

# Copy app source
COPY . .
RUN npm run build

# ── Stage 2: Serve with Nginx ─────────────────────────────────
FROM nginx:1.27-alpine

# Copy built assets
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]