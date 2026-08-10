"""Yahoo API module for ScrapeBadger SDK.

This module provides a comprehensive async client for scraping
search.yahoo.com through the ScrapeBadger API. All methods are async and
return strongly-typed Pydantic models.

Example:
    ```python
    from scrapebadger import ScrapeBadger

    async with ScrapeBadger(api_key="your-key") as client:
        # Web search
        results = await client.yahoo.search.search("coffee machine")
        for r in results.results:
            print(f"{r.position}. {r.title} — {r.url}")

        # Images
        images = await client.yahoo.media.images("cats")

        # News
        news = await client.yahoo.news.news("ai")
    ```
"""

from scrapebadger.yahoo.client import YahooClient
from scrapebadger.yahoo.media import MediaClient
from scrapebadger.yahoo.models import (
    Ad,
    AutocompleteResponse,
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
from scrapebadger.yahoo.news import NewsClient
from scrapebadger.yahoo.reference import ReferenceClient
from scrapebadger.yahoo.search import SearchClient

__all__ = [
    "Ad",
    "AutocompleteResponse",
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
    "YahooClient",
]
