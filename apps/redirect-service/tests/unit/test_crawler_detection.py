"""Tests for crawler user-agent detection."""

import pytest

from redirect_service.crawler_detection import is_crawler


class TestIsCrawler:
    @pytest.mark.parametrize(
        "user_agent",
        [
            "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)",
            "Facebot",
            "Twitterbot/1.0",
            "LinkedInBot/1.0 (compatible; Mozilla/5.0; Apache-HttpClient +http://www.linkedin.com)",
            "Slackbot-LinkExpanding 1.0 (+https://api.slack.com/robots)",
            "WhatsApp/2.23.20.0 A",
            "Discordbot/2.0; +https://discordapp.com",
            "TelegramBot (like TwitterBot)",
            "Googlebot/2.1 (+http://www.google.com/bot.html)",
            "bingbot/2.0; +http://www.bing.com/bingbot.htm",
            "Applebot/0.1 (+http://www.apple.com/go/applebot)",
            # Case-insensitive
            "FACEBOOKEXTERNALHIT/1.1",
            "twitterbot/1.0",
            "SLACKBOT-LINKEXPANDING",
        ],
    )
    def test_known_crawlers_detected(self, user_agent: str) -> None:
        assert is_crawler(user_agent) is True

    @pytest.mark.parametrize(
        "user_agent",
        [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",  # noqa: E501
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",  # noqa: E501
            "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)",
            "curl/7.88.1",
            "PostmanRuntime/7.36.0",
        ],
    )
    def test_browsers_not_detected(self, user_agent: str) -> None:
        assert is_crawler(user_agent) is False

    def test_none_user_agent_returns_false(self) -> None:
        assert is_crawler(None) is False

    def test_empty_string_returns_false(self) -> None:
        assert is_crawler("") is False
