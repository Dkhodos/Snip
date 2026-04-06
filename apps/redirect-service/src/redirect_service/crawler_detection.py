"""Crawler / social bot user-agent detection."""

_CRAWLER_SUBSTRINGS = [
    "facebookexternalhit",
    "facebot",
    "twitterbot",
    "linkedinbot",
    "slackbot",
    "whatsapp",
    "discordbot",
    "telegrambot",
    "googlebot",
    "bingbot",
    "applebot",
    "pinterest",
    "embedly",
    "outbrain",
    "quora link preview",
    "rogerbot",
    "showyoubot",
    "skypeuripreview",
    "vkshare",
    "w3c_validator",
    "xing-contenttabreceiver",
    "iframely",
]


def is_crawler(user_agent: str | None) -> bool:
    """Return True if the user-agent belongs to a known social crawler or link preview bot."""
    if not user_agent:
        return False
    ua_lower = user_agent.lower()
    return any(substring in ua_lower for substring in _CRAWLER_SUBSTRINGS)
