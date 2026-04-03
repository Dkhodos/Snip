"""Tests for the dev analytics client."""

from datetime import UTC, datetime, timedelta

import pytest

from snip_analytics.models import ClickEventRow
from snip_analytics.providers.dev.client import DevAnalyticsClient


def _make_event(
    *,
    event_id: str = "evt-1",
    link_id: str = "link-1",
    short_code: str = "abc",
    org_id: str = "org-1",
    clicked_at: datetime | None = None,
    user_agent: str | None = None,
    country: str | None = None,
) -> ClickEventRow:
    return ClickEventRow(
        event_id=event_id,
        link_id=link_id,
        short_code=short_code,
        org_id=org_id,
        clicked_at=clicked_at or datetime.now(tz=UTC),
        user_agent=user_agent,
        country=country,
    )


class TestDevAnalyticsClient:
    """Tests for DevAnalyticsClient."""

    @pytest.fixture()
    def client(self) -> DevAnalyticsClient:
        return DevAnalyticsClient()

    async def test_insert_click_event_stores_event(self, client: DevAnalyticsClient) -> None:
        event = _make_event()
        await client.insert_click_event(event)
        assert len(client._events) == 1
        assert client._events[0] is event

    async def test_insert_multiple_events(self, client: DevAnalyticsClient) -> None:
        await client.insert_click_event(_make_event(event_id="e1"))
        await client.insert_click_event(_make_event(event_id="e2"))
        await client.insert_click_event(_make_event(event_id="e3"))
        assert len(client._events) == 3

    async def test_get_daily_clicks_for_link_filters_by_link_id(
        self, client: DevAnalyticsClient
    ) -> None:
        now = datetime.now(tz=UTC)
        await client.insert_click_event(_make_event(link_id="link-1", clicked_at=now))
        await client.insert_click_event(_make_event(link_id="link-1", clicked_at=now))
        await client.insert_click_event(_make_event(link_id="link-2", clicked_at=now))

        results = await client.get_daily_clicks_for_link("link-1")
        total = sum(r.count for r in results)
        assert total == 2

    async def test_get_daily_clicks_for_org_filters_by_org_id(
        self, client: DevAnalyticsClient
    ) -> None:
        now = datetime.now(tz=UTC)
        await client.insert_click_event(_make_event(org_id="org-1", clicked_at=now))
        await client.insert_click_event(_make_event(org_id="org-1", clicked_at=now))
        await client.insert_click_event(_make_event(org_id="org-2", clicked_at=now))

        results = await client.get_daily_clicks_for_org("org-1")
        total = sum(r.count for r in results)
        assert total == 2

    async def test_empty_results_for_unknown_link(self, client: DevAnalyticsClient) -> None:
        await client.insert_click_event(_make_event(link_id="link-1"))
        results = await client.get_daily_clicks_for_link("unknown-link")
        assert results == []

    async def test_empty_results_for_unknown_org(self, client: DevAnalyticsClient) -> None:
        await client.insert_click_event(_make_event(org_id="org-1"))
        results = await client.get_daily_clicks_for_org("unknown-org")
        assert results == []

    async def test_date_filtering_excludes_old_events(self, client: DevAnalyticsClient) -> None:
        now = datetime.now(tz=UTC)
        old = now - timedelta(days=10)

        await client.insert_click_event(
            _make_event(event_id="recent", link_id="link-1", clicked_at=now)
        )
        await client.insert_click_event(
            _make_event(event_id="old", link_id="link-1", clicked_at=old)
        )

        results = await client.get_daily_clicks_for_link("link-1", days=7)
        total = sum(r.count for r in results)
        assert total == 1

    async def test_daily_clicks_returns_sorted_dates(self, client: DevAnalyticsClient) -> None:
        now = datetime.now(tz=UTC)
        yesterday = now - timedelta(days=1)

        await client.insert_click_event(
            _make_event(event_id="e1", link_id="link-1", clicked_at=now)
        )
        await client.insert_click_event(
            _make_event(event_id="e2", link_id="link-1", clicked_at=yesterday)
        )

        results = await client.get_daily_clicks_for_link("link-1")
        dates = [r.date for r in results]
        assert dates == sorted(dates)
