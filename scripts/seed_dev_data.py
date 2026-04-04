#!/usr/bin/env python3
"""Seed development data into the local database.

Usage (from repo root):
    uv run --package dashboard-backend python scripts/seed_dev_data.py
    uv run --package dashboard-backend python scripts/seed_dev_data.py --org-id my_org

Requires DATABASE_URL (or ENVIRONMENT=development with default SQLite URL) to be set.
"""

import argparse
import asyncio

from dashboard_backend.config import settings
from dashboard_backend.managers.seed_manager import SeedManager
from snip_db.engine import create_engine, create_session_factory, init_session_factory
from snip_db.stores.click_event_store import ClickEventStore
from snip_db.stores.link_store import LinkStore


async def main(org_id: str) -> None:
    engine = create_engine(settings.effective_database_url)
    session_factory = create_session_factory(engine)
    init_session_factory(session_factory)

    async with session_factory() as session:
        manager = SeedManager(
            link_store=LinkStore(session),
            click_event_store=ClickEventStore(session),
        )
        result = await manager.seed(org_id)
        print(result)

    await engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed development data")
    parser.add_argument("--org-id", default="dev_org", help="Organisation ID to seed data for")
    args = parser.parse_args()
    asyncio.run(main(args.org_id))
