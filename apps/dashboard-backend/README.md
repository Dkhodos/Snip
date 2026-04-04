# Dashboard Backend

FastAPI REST API for link management, user authentication, and click analytics.

## Routes

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/links` | Create a short link |
| `GET` | `/links` | List links (paginated, searchable) |
| `GET` | `/links/{link_id}` | Get link by ID |
| `PATCH` | `/links/{link_id}` | Update link |
| `DELETE` | `/links/{link_id}` | Soft-delete link |
| `GET` | `/links/{link_id}/clicks` | Click history for a link |
| `GET` | `/clicks/aggregate` | Aggregated click analytics |
| `GET` | `/health` | Health check |

## Dependencies

Uses shared packages: `snip-db`, `snip-auth`, `snip-email`, `snip-logger`.

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | — | PostgreSQL connection string |
| `ENVIRONMENT` | `development` | `development` / `staging` / `production` |
| `CLERK_PUBLISHABLE_KEY` | — | Clerk public key |
| `CLERK_SECRET_KEY` | — | Clerk secret (omit for dev bypass) |
| `EMAIL_PROVIDER` | `mailpit` | `mailpit` / `resend` |
| `RESEND_API_KEY` | — | Resend API key (prod) |
| `ALLOWED_ORIGINS` | `http://localhost:5173` | CORS origins |
| `CLICK_THRESHOLD` | `100` | Click count alert threshold |

## Running

```bash
make dashboard-backend:install
make dashboard-backend:lint
make dashboard-backend:test:unit
```

Port: **8080**
