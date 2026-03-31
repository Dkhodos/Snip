"""Database engine and session management."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# Module-level session factory, set by the application at startup
_session_factory: async_sessionmaker[AsyncSession] | None = None


def create_engine(url: str, **kwargs: object) -> AsyncEngine:
    """Create an async SQLAlchemy engine."""
    return create_async_engine(url, echo=False, **kwargs)


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Create an async session factory bound to the given engine."""
    return async_sessionmaker(engine, expire_on_commit=False)


def init_session_factory(factory: async_sessionmaker[AsyncSession]) -> None:
    """Initialize the module-level session factory. Call once at app startup."""
    global _session_factory
    _session_factory = factory


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an async session."""
    if _session_factory is None:
        msg = "Database session factory not initialized. Call init_session_factory() first."
        raise RuntimeError(msg)
    async with _session_factory() as session:
        yield session
