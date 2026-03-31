"""Shared fixtures for all tests."""

import pytest
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    async_sessionmaker,
    create_async_engine,
)

from snip_db.models.base import Base

_TEST_DATABASE_URL = "sqlite+aiosqlite://"


@pytest.fixture(scope="session")
async def _engine():
    """Create a single async engine for the entire test session."""
    engine = create_async_engine(_TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture()
async def _db_connection(_engine):
    """One connection per test, wrapped in a transaction that will be rolled back."""
    async with _engine.connect() as connection:
        transaction = await connection.begin()
        yield connection
        await transaction.rollback()


@pytest.fixture()
async def _db_session(_db_connection: AsyncConnection):
    """A session using SAVEPOINT so store .commit() calls don't escape the test transaction."""
    session_factory = async_sessionmaker(
        bind=_db_connection,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )
    async with session_factory() as session:
        yield session
