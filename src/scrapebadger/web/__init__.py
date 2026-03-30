"""Web scraping module for ScrapeBadger SDK."""

from scrapebadger.web.client import WebClient
from scrapebadger.web.models import DetectResult, ScrapeResult

__all__ = [
    "DetectResult",
    "ScrapeResult",
    "WebClient",
]
