"""snip-analytics: shared analytics client package."""

from snip_analytics.factory import create_analytics_client
from snip_analytics.models import ClickEventRow, DailyClickCount
from snip_analytics.protocol import AnalyticsClient
from snip_analytics.provider import AnalyticsProvider

__all__ = [
    "AnalyticsClient",
    "AnalyticsProvider",
    "ClickEventRow",
    "DailyClickCount",
    "create_analytics_client",
]
