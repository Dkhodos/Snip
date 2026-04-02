"""Link data access store."""

import logging
from datetime import datetime
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import delete, func, select

from snip_db.models import Link
from snip_db.stores.base_store import BaseStore

_log = logging.getLogger(__name__)


class LinkStore(BaseStore[Link]):
    model = Link

    async def create(
        self,
        *,
        org_id: str,
        short_code: str,
        target_url: str,
        title: str,
        created_by: str,
        click_count: int = 0,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        expires_at: Optional[datetime] = None,
        link_id: Optional[UUID] = None,
    ) -> Link:
        kwargs: dict = {
            "org_id": org_id,
            "short_code": short_code,
            "target_url": target_url,
            "title": title,
            "created_by": created_by,
            "click_count": click_count,
            "is_active": is_active,
        }
        if link_id is not None:
            kwargs["id"] = link_id
        if created_at is not None:
            kwargs["created_at"] = created_at
        if expires_at is not None:
            kwargs["expires_at"] = expires_at

        link = Link(**kwargs)
        self._add(link)
        await self._flush_and_refresh(link)
        _log.info("link_created short_code=%s org_id=%s", short_code, org_id)
        return link

    async def get_by_id(self, link_id: UUID, org_id: str) -> Optional[Link]:
        return await self._get_one_or_none(Link.id == link_id, Link.org_id == org_id)

    async def get_by_short_code(
        self, short_code: str, *, active_only: bool = False
    ) -> Optional[Link]:
        conditions = [Link.short_code == short_code]
        if active_only:
            conditions.append(Link.is_active.is_(True))
        return await self._get_one_or_none(*conditions)

    async def list(
        self,
        org_id: str,
        *,
        page: int = 1,
        limit: int = 20,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        status: Optional[str] = None,
    ) -> Tuple[List[Link], int]:
        base_filter = [Link.org_id == org_id]

        if search:
            pattern = f"%{search}%"
            base_filter.append((Link.title.ilike(pattern)) | (Link.short_code.ilike(pattern)))

        if status == "active":
            base_filter.append(Link.is_active.is_(True))
        elif status == "inactive":
            base_filter.append(Link.is_active.is_(False))
        elif status == "expired":
            base_filter.append(Link.expires_at < datetime.utcnow())

        # Count
        count_query = select(func.count()).select_from(Link).where(*base_filter)
        total = (await self._session.execute(count_query)).scalar_one()

        # Sort
        sort_column = getattr(Link, sort_by)
        order = sort_column.asc() if sort_order == "asc" else sort_column.desc()

        # Fetch
        offset = (page - 1) * limit
        query = select(Link).where(*base_filter).order_by(order).offset(offset).limit(limit)
        result = await self._session.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def update(self, link: Link, **fields: object) -> Link:
        for field, value in fields.items():
            setattr(link, field, value)
        result = await self._flush_and_refresh(link)
        _log.info("link_updated link_id=%s fields=%s", link.id, list(fields.keys()))
        return result

    async def soft_delete(self, link: Link) -> None:
        link.is_active = False
        await self.flush()
        _log.info("link_soft_deleted link_id=%s", link.id)

    async def increment_click_count(self, link: Link) -> None:
        link.click_count = Link.click_count + 1  # type: ignore[assignment]
        await self.flush()
        _log.debug("click_count_incremented link_id=%s", link.id)

    async def get_stats(self, org_id: str) -> dict:
        base = select(Link).where(Link.org_id == org_id)

        total = (
            await self._session.execute(select(func.count()).select_from(base.subquery()))
        ).scalar_one()

        clicks = (
            await self._session.execute(
                select(func.coalesce(func.sum(Link.click_count), 0)).where(Link.org_id == org_id)
            )
        ).scalar_one()

        active = (
            await self._session.execute(
                select(func.count()).where(Link.org_id == org_id, Link.is_active.is_(True))
            )
        ).scalar_one()

        expired = (
            await self._session.execute(
                select(func.count()).where(
                    Link.org_id == org_id, Link.expires_at < datetime.utcnow()
                )
            )
        ).scalar_one()

        return {
            "total_links": total,
            "total_clicks": clicks,
            "active_links": active,
            "expired_links": expired,
        }

    async def get_ids_by_org(self, org_id: str) -> List[UUID]:
        result = await self._session.execute(select(Link.id).where(Link.org_id == org_id))
        return [row[0] for row in result.all()]

    async def delete_by_org(self, org_id: str) -> None:
        await self._session.execute(delete(Link).where(Link.org_id == org_id))
