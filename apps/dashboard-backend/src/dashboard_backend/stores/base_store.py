"""Base store with shared session management and common operations."""

from snip_db.models.base import Base
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class BaseStore[T: Base]:
    """Abstract base for all data access stores.

    Provides session management, commit, and reusable query helpers.
    Subclasses set ``model`` to their SQLAlchemy model class.
    """

    model: type[T]

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def commit(self) -> None:
        await self._session.commit()

    async def flush(self) -> None:
        await self._session.flush()

    # --- common helpers ---

    def _add(self, entity: T) -> None:
        self._session.add(entity)

    async def _flush_and_refresh(self, entity: T) -> T:
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def _get_one_or_none(self, *conditions: object) -> T | None:
        query = select(self.model).where(*conditions)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def _get_all(self) -> list[T]:
        result = await self._session.execute(select(self.model))
        return list(result.scalars().all())
