"""Bing API module for ScrapeBadger SDK.

This module provides a comprehensive async client for scraping bing.com
through the ScrapeBadger API. All methods are async and return strongly-typed
Pydantic models.

Example:
    ```python
    from scrapebadger import ScrapeBadger

    async with ScrapeBadger(api_key="your-key") as client:
        # Web search
        results = await client.bing.search.search("coffee machine")
        for r in results.results:
            print(f"{r.position}. {r.title} — {r.url}")

        # Images
        images = await client.bing.media.images("cats")

        # News
        news = await client.bing.news.news("ai", freshness="day")
    ```
"""

from scrapebadger.bing.client import BingClient
from scrapebadger.bing.media import MediaClient
from scrapebadger.bing.models import (
    Ad,
    AutocompleteResponse,
    DeepLink,
    ImageResult,
    ImagesResponse,
    Market,
    MarketsResponse,
    NewsArticle,
    NewsResponse,
    OrganicResult,
    SearchResponse,
    VideoResult,
    VideosResponse,
)
from scrapebadger.bing.news import NewsClient
from scrapebadger.bing.reference import ReferenceClient
from scrapebadger.bing.search import SearchClient

__all__ = [
    "Ad",
    "AutocompleteResponse",
    "BingClient",
    "DeepLink",
    "ImageResult",
    "ImagesResponse",
    "Market",
    "MarketsResponse",
    "MediaClient",
    "NewsArticle",
    "NewsClient",
    "NewsResponse",
    "OrganicResult",
    "ReferenceClient",
    "SearchClient",
    "SearchResponse",
    "VideoResult",
    "VideosResponse",
]
