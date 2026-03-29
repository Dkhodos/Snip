"""Development seed data router."""

import random
from datetime import datetime, timedelta
from uuid import uuid4

import shortuuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from dashboard_backend.config import settings
from snip_db import get_session
from snip_db.models import ClickEvent, Link

router = APIRouter(tags=["seed"])

SAMPLE_TITLES = [
    "Marketing Campaign Q1",
    "Product Launch Blog",
    "Social Media Bio Link",
    "Developer Docs",
    "Black Friday Sale",
    "Summer Promo Landing",
    "Newsletter Signup",
    "Referral Program",
    "API Documentation",
    "Customer Support Portal",
    "Company Blog",
    "Careers Page",
    "Press Kit Download",
    "Webinar Registration",
    "Case Study - Enterprise",
    "Partner Program",
    "Pricing Page A/B Test",
    "Mobile App Download",
    "YouTube Channel",
    "Podcast Episode 42",
    "Conference Talk Slides",
    "Open Source Repo",
    "Feature Request Board",
    "Status Page",
    "Annual Report 2025",
]

SAMPLE_URLS = [
    "https://example.com/marketing/q1-campaign",
    "https://blog.example.com/product-launch",
    "https://example.com/bio",
    "https://docs.example.com/developers",
    "https://shop.example.com/black-friday",
    "https://example.com/summer-promo",
    "https://example.com/newsletter",
    "https://example.com/referral",
    "https://api.example.com/docs",
    "https://support.example.com",
    "https://blog.example.com",
    "https://example.com/careers",
    "https://example.com/press",
    "https://events.example.com/webinar",
    "https://example.com/case-studies/enterprise",
    "https://partners.example.com",
    "https://example.com/pricing",
    "https://example.com/app",
    "https://youtube.com/@example",
    "https://podcast.example.com/ep42",
    "https://slides.example.com/conf-2025",
    "https://github.com/example/oss",
    "https://feedback.example.com",
    "https://status.example.com",
    "https://example.com/annual-report-2025",
]

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)",
    "Mozilla/5.0 (Linux; Android 14)",
    None,
]

COUNTRIES = ["US", "GB", "DE", "FR", "JP", "BR", "IN", "CA", "AU", None]


def _weighted_random_time(now: datetime, days_back: int) -> datetime:
    """Generate a random timestamp weighted toward more recent days."""
    # Use exponential distribution so recent days get more clicks
    day_offset = min(int(random.expovariate(0.15)), days_back)
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return now - timedelta(days=day_offset, hours=hour, minutes=minute, seconds=second)


@router.post("/seed")
async def seed_data(
    session: AsyncSession = Depends(get_session),
) -> dict:
    if settings.environment != "development":
        raise HTTPException(status_code=403, detail="Seed endpoint is only available in development")

    org_id = "dev_org"
    now = datetime.utcnow()

    # Delete existing dev data (click_events first due to FK constraint)
    existing_links = await session.execute(select(Link.id).where(Link.org_id == org_id))
    link_ids = [row[0] for row in existing_links.all()]
    if link_ids:
        await session.execute(delete(ClickEvent).where(ClickEvent.link_id.in_(link_ids)))
    await session.execute(delete(Link).where(Link.org_id == org_id))

    # Create 25 links
    links_created = []
    for i in range(25):
        click_count = random.randint(0, 500)
        is_active = random.random() < 0.8

        # Determine expiry
        expires_at = None
        if i < 5:
            # Expired links (expires_at in the past)
            expires_at = now - timedelta(days=random.randint(1, 30))
        elif i < 10:
            # Future expiry
            expires_at = now + timedelta(days=random.randint(1, 90))

        link = Link(
            id=uuid4(),
            org_id=org_id,
            short_code=shortuuid.uuid()[:8],
            target_url=SAMPLE_URLS[i],
            title=SAMPLE_TITLES[i],
            click_count=click_count,
            is_active=is_active,
            created_by="dev_user",
            created_at=now - timedelta(days=random.randint(1, 60)),
            expires_at=expires_at,
        )
        session.add(link)
        links_created.append((link, click_count))

    # Flush to ensure link IDs are available
    await session.flush()

    # Create click events for each link
    for link, click_count in links_created:
        for _ in range(click_count):
            event = ClickEvent(
                id=uuid4(),
                link_id=link.id,
                clicked_at=_weighted_random_time(now, 30),
                user_agent=random.choice(USER_AGENTS),
                country=random.choice(COUNTRIES),
            )
            session.add(event)

    await session.commit()

    return {"message": "Seeded 25 links with click events", "links_created": 25}
