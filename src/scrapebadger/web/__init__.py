"""Web scraping module for ScrapeBadger SDK."""

from scrapebadger.web.client import WebClient
from scrapebadger.web.models import DetectResult, ExtractResult, ScrapeResult, ScreenshotResult

__all__ = [
    "DetectResult",
    "ExtractResult",
    "ScrapeResult",
    "ScreenshotResult",
    "WebClient",
]
