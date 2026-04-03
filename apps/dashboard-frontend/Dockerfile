# Build stage
FROM node:25-slim AS builder

RUN npm install -g pnpm@10.17.1

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
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY apps/dashboard-frontend/nginx.conf.template /etc/nginx/conf.d/default.conf.template
COPY apps/dashboard-frontend/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

EXPOSE 8080

CMD ["/docker-entrypoint.sh"]

