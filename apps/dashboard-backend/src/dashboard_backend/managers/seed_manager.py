"""Development seed data manager."""

import random
from datetime import datetime, timedelta
from uuid import uuid4

import shortuuid
from snip_db.stores.click_event_store import ClickEventStore
from snip_db.stores.link_store import LinkStore

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
    day_offset = min(int(random.expovariate(0.15)), days_back)
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return now - timedelta(days=day_offset, hours=hour, minutes=minute, seconds=second)


class SeedManager:
    def __init__(self, link_store: LinkStore, click_event_store: ClickEventStore) -> None:
        self._link_store = link_store
        self._click_event_store = click_event_store

    async def seed(self, org_id: str) -> dict:
        now = datetime.utcnow()

        # Delete existing dev data (click_events first due to FK constraint)
        link_ids = await self._link_store.get_ids_by_org(org_id)
        await self._click_event_store.delete_by_link_ids(link_ids)
        await self._link_store.delete_by_org(org_id)

        # Create 25 links with click events
        for i in range(25):
            click_count = random.randint(0, 500)
            is_active = random.random() < 0.8

            expires_at = None
            if i < 5:
                expires_at = now - timedelta(days=random.randint(1, 30))
            elif i < 10:
                expires_at = now + timedelta(days=random.randint(1, 90))

            link_id = uuid4()
            link = await self._link_store.create(
                link_id=link_id,
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

            for _ in range(click_count):
                await self._click_event_store.create(
                    event_id=uuid4(),
                    link_id=link.id,
                    clicked_at=_weighted_random_time(now, 30),
                    user_agent=random.choice(USER_AGENTS),
                    country=random.choice(COUNTRIES),
                )

        await self._link_store.commit()

        return {"message": "Seeded 25 links with click events", "links_created": 25}
