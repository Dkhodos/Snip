"""Link business logic manager."""

from typing import List, Optional, Tuple

import shortuuid
from snip_db.models import Link
from snip_db.stores.link_store import LinkStore

from dashboard_backend.exceptions import (
    InvalidSortFieldError,
    LinkNotFoundError,
    ShortCodeCollisionError,
)

ALLOWED_SORT_FIELDS = {"created_at", "click_count", "title"}


class LinkManager:
    def __init__(self, link_store: LinkStore) -> None:
        self._link_store = link_store

    async def create_link(
        self,
        *,
        org_id: str,
        user_id: str,
        target_url: str,
        title: str,
        custom_short_code: Optional[str] = None,
    ) -> Link:
        short_code = custom_short_code or shortuuid.uuid()[:8]

        existing = await self._link_store.get_by_short_code(short_code)
        if existing:
            raise ShortCodeCollisionError()

        link = await self._link_store.create(
            org_id=org_id,
            short_code=short_code,
            target_url=target_url,
            title=title,
            created_by=user_id,
        )
        await self._link_store.commit()
        return link

    async def list_links(
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
        if sort_by not in ALLOWED_SORT_FIELDS:
            raise InvalidSortFieldError(ALLOWED_SORT_FIELDS)

        return await self._link_store.list(
            org_id,
            page=page,
            limit=limit,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
            status=status,
        )

    async def get_link(self, link_id: object, org_id: str) -> Link:
        link = await self._link_store.get_by_id(link_id, org_id)  # type: ignore[arg-type]
        if not link:
            raise LinkNotFoundError()
        return link

    async def update_link(self, link_id: object, org_id: str, **fields: object) -> Link:
        link = await self.get_link(link_id, org_id)
        updated = await self._link_store.update(link, **fields)
        await self._link_store.commit()
        return updated

    async def delete_link(self, link_id: object, org_id: str) -> None:
        link = await self.get_link(link_id, org_id)
        await self._link_store.soft_delete(link)
        await self._link_store.commit()

    async def get_stats(self, org_id: str) -> dict:
        return await self._link_store.get_stats(org_id)
