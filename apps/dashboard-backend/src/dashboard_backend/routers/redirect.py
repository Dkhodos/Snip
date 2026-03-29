"""Public redirect endpoint."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from snip_db import get_session
from snip_db.models import ClickEvent, Link

router = APIRouter(tags=["redirect"])


@router.get("/r/{short_code}")
async def redirect_to_target(
    short_code: str,
    session: AsyncSession = Depends(get_session),
) -> RedirectResponse:
    query = select(Link).where(Link.short_code == short_code, Link.is_active.is_(True))
    result = await session.execute(query)
    link = result.scalar_one_or_none()

    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    # Check expiry
    if link.expires_at and link.expires_at < datetime.utcnow():
        raise HTTPException(status_code=410, detail="Link has expired")

    # Increment click count atomically
    link.click_count = Link.click_count + 1

    # Record click event
    click = ClickEvent(link_id=link.id, clicked_at=datetime.utcnow())
    session.add(click)

    await session.commit()

    return RedirectResponse(url=link.target_url, status_code=302)
