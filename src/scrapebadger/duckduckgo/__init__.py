"""DuckDuckGo API module for ScrapeBadger SDK.

This module provides an async client for scraping DuckDuckGo through the
ScrapeBadger API — web search, images, news, videos, autocomplete, instant
answers, and the supported region list. All methods are async and return
strongly-typed Pydantic models.

Example:
    ```python
    from scrapebadger import ScrapeBadger

    async with ScrapeBadger(api_key="your-key") as client:
        # Web search
        results = await client.duckduckgo.search.search("python asyncio")
        for r in results.results:
            print(r.title, r.url)

        # Images
        images = await client.duckduckgo.media.images("golden retriever")

        # Instant answer
        answer = await client.duckduckgo.reference.instant("pi")
        print(answer.answer)
    ```
"""

from scrapebadger.duckduckgo.client import DuckDuckGoClient
from scrapebadger.duckduckgo.media import MediaClient
from scrapebadger.duckduckgo.models import (
    AbstractBox,
    AutocompleteResponse,
    ImageResponse,
    ImageResult,
    InstantAnswerResponse,
    InstantAnswerTopic,
    NewsResponse,
    NewsResult,
    Region,
    RegionsResponse,
    SearchResponse,
    SearchResult,
    VideoResponse,
    VideoResult,
)
from scrapebadger.duckduckgo.reference import ReferenceClient
from scrapebadger.duckduckgo.search import SearchClient

__all__ = [
    "AbstractBox",
    "AutocompleteResponse",
    "DuckDuckGoClient",
    "ImageResponse",
    "ImageResult",
    "InstantAnswerResponse",
    "InstantAnswerTopic",
    "MediaClient",
    "NewsResponse",
    "NewsResult",
    "ReferenceClient",
    "Region",
    "RegionsResponse",
    "SearchClient",
    "SearchResponse",
    "SearchResult",
    "VideoResponse",
    "VideoResult",
]
