"""Baidu API module for ScrapeBadger SDK.

This module provides an async client for scraping Baidu — China's #1 search
engine (~60% market share) — through the ScrapeBadger API. All methods are
async and return strongly-typed Pydantic models.

Results carry the **real target URL** in ``url``, decoded from Baidu's ``mu``
attribute; the ``baidu.com/link?url=`` tracking redirect is kept separately in
``baidu_url``.

Example:
    ```python
    from scrapebadger import ScrapeBadger

    async with ScrapeBadger(api_key="your-key") as client:
        # Web search
        results = await client.baidu.search("咖啡机")
        for r in results.results:
            print(f"{r.position}. {r.title} — {r.url}")

        # News, sorted most-recent first
        news = await client.baidu.news("人工智能", sort="time")

        # Images
        images = await client.baidu.images("猫")

        # Search-box suggestions
        suggestions = await client.baidu.autocomplete("咖啡")
    ```
"""

from scrapebadger.baidu.client import BaiduClient
from scrapebadger.baidu.models import (
    AutocompleteResponse,
    ImageResult,
    ImagesResponse,
    NewsResponse,
    NewsResult,
    OrganicResult,
    RelatedSearch,
    SearchResponse,
    Suggestion,
)

__all__ = [
    # Autocomplete
    "AutocompleteResponse",
    # Client
    "BaiduClient",
    # Images
    "ImageResult",
    "ImagesResponse",
    # News
    "NewsResponse",
    "NewsResult",
    # Web search
    "OrganicResult",
    "RelatedSearch",
    "SearchResponse",
    "Suggestion",
]
