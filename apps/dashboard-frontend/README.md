# Dashboard Frontend

React SPA for managing short links and viewing click analytics.

## Tech

- React 19 + TypeScript
- TanStack Router + React Query
- Radix UI + Tailwind CSS
- Clerk (authentication)
- Recharts (analytics charts)
- Vite (build)

## Configuration

Build-time (baked into bundle):

| Variable | Description |
|----------|-------------|
| `VITE_CLERK_PUBLISHABLE_KEY` | Clerk public key |
| `VITE_API_URL` | Backend API base URL |
| `VITE_REDIRECT_BASE_URL` | Base URL for generated short links |

Runtime (Docker/nginx):

| Variable | Description |
|----------|-------------|
| `BACKEND_URL` | Backend service URL (reverse proxy target) |

## Running

```bash
make dashboard-frontend:install
make dashboard-frontend:dev           # Vite dev server on :5173
make dashboard-frontend:build         # Production build
make dashboard-frontend:lint
make dashboard-frontend:test
```

Dev server proxies `/api` to `localhost:8080`.
