# Build stage
ARG BASE_REGISTRY
FROM ${BASE_REGISTRY}/snip-base/node-base:latest AS builder

WORKDIR /app

# Install dependencies (cached layer)
COPY apps/dashboard-frontend/package.json apps/dashboard-frontend/pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

# Copy source
COPY apps/dashboard-frontend/ .

# Build-time env vars — baked into the bundle by Vite
ARG VITE_CLERK_PUBLISHABLE_KEY
ARG VITE_API_URL
ARG VITE_REDIRECT_BASE_URL

RUN pnpm build

# Serve stage
FROM ${BASE_REGISTRY}/snip-base/nginx-base:latest

COPY --from=builder /app/dist /usr/share/nginx/html
COPY apps/dashboard-frontend/nginx.conf.template /etc/nginx/conf.d/default.conf.template
COPY apps/dashboard-frontend/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

EXPOSE 8080

CMD ["/docker-entrypoint.sh"]

