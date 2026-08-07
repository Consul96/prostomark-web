# ─────────────────────────────────────────────────────────────────────────────
# Stage 1 — build the static bundle with Vite.
# Build context is the REPO ROOT (see docker-compose: build.context: .) so this
# stage can also reach infra/nginx for the runtime stage below.
# ─────────────────────────────────────────────────────────────────────────────
FROM node:22-alpine AS build

WORKDIR /app

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build   # tsc --noEmit && vite build → produces /app/dist

# ─────────────────────────────────────────────────────────────────────────────
# Stage 2 — serve `dist/` with nginx. No Node, no vite preview in production.
# nginx also reverse-proxies /api/ to the backend (see infra/nginx/default.conf).
# ─────────────────────────────────────────────────────────────────────────────
FROM nginx:1.27-alpine AS runtime

# Static build output.
COPY --from=build /app/dist /usr/share/nginx/html

# Site config (static assets caching + SPA fallback + gzip + /api proxy).
COPY infra/nginx/default.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
