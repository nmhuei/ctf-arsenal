FROM node:22-bookworm-slim@sha256:f32b81066cde10a75dbac96646099533316d94bac4150c55da1636e1f0ffdc46 AS frontend-builder

WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM caddy:2.11.4-alpine@sha256:5f5c8640aae01df9654968d946d8f1a56c497f1dd5c5cda4cf95ab7c14d58648

COPY caddy/Caddyfile /etc/caddy/Caddyfile
COPY --from=frontend-builder /frontend/dist/client/. /srv/public/

RUN mkdir -p /srv/public/avatars

VOLUME ["/data", "/config", "/run/php", "/srv/public/avatars"]

EXPOSE 80 443 443/udp
