"""Web scraping module for ScrapeBadger SDK."""

from scrapebadger.web.client import WebClient
from scrapebadger.web.models import (
    BatchResult,
    ExtractResult,
    ScrapeResult,
    ScreenshotResult,
    SessionInfo,
)

__all__ = [
    "BatchResult",
    "ExtractResult",
    "ScrapeResult",
    "ScreenshotResult",
    "SessionInfo",
    "WebClient",
]
