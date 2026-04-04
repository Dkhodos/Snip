# snip-db

SQLAlchemy 2.0 persistence layer with async PostgreSQL support and Alembic migrations.

## Models

- **Link** — short code, target URL, org ownership, click count, expiry, soft-delete
- **ClickEvent** — per-click record with timestamp, user agent, country
- **FeatureFlag** — org-scoped feature toggles

## Stores

Repository-pattern data access:

- `LinkStore` — CRUD, search, pagination, soft-delete, `increment_click_count`
- `ClickEventStore` — create, daily aggregates per link/org
- `FeatureFlagStore` — generic CRUD via `BaseStore`

## Usage

```python
from snip_db.engine import create_engine, create_session_factory, get_session
from snip_db.stores.link_store import LinkStore
```

## Migrations

```bash
make db:migrate          # apply pending migrations
make db:migrate:create   # generate new migration
```

Migrations live in `src/snip_db/migrations/versions/`.

## Extras

Install with `snip-db[pg]` to include the `asyncpg` driver.
