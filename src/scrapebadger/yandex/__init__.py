"""Yandex API module for ScrapeBadger SDK.

This module provides an async client for scraping Yandex through the
ScrapeBadger API — web search, image search, reverse-image (CBIR) search, and
the supported market list. All methods are async and return strongly-typed
Pydantic models.

Example:
    ```python
    from scrapebadger import ScrapeBadger

    async with ScrapeBadger(api_key="your-key") as client:
        # Web search
        results = await client.yandex.search.search("python asyncio")
        for r in results.organic_results:
            print(r.title, r.url)

        # Images
        images = await client.yandex.images.search("golden retriever")

        # Reverse image
        reverse = await client.yandex.images.reverse(
            "https://example.com/photo.jpg"
        )

        # Markets
        markets = await client.yandex.reference.markets()
    ```
"""

from scrapebadger.yandex.client import YandexClient
from scrapebadger.yandex.images import ImagesClient
from scrapebadger.yandex.models import (
    Image,
    ImageResult,
    ImagesResponse,
    Market,
    MarketsResponse,
    OrganicResult,
    OtherSize,
    Pagination,
    ReverseImageResponse,
    ReverseSite,
    SearchResponse,
    SimilarImage,
    Sitelink,
    Tag,
)
from scrapebadger.yandex.reference import ReferenceClient
from scrapebadger.yandex.search import SearchClient

__all__ = [
    "Image",
    "ImageResult",
    "ImagesClient",
    "ImagesResponse",
    "Market",
    "MarketsResponse",
    "OrganicResult",
    "OtherSize",
    "Pagination",
    "ReferenceClient",
    "ReverseImageResponse",
    "ReverseSite",
    "SearchClient",
    "SearchResponse",
    "SimilarImage",
    "Sitelink",
    "Tag",
    "YandexClient",
]
