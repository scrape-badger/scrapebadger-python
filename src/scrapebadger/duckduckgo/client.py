"""DuckDuckGo API client combining all sub-clients.

This module provides the main DuckDuckGoClient class that serves as the
entry point for all DuckDuckGo API operations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from scrapebadger.duckduckgo.media import MediaClient
from scrapebadger.duckduckgo.reference import ReferenceClient
from scrapebadger.duckduckgo.search import SearchClient

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class DuckDuckGoClient:
    """Client for all DuckDuckGo API operations.

    This class provides access to all DuckDuckGo scraping endpoints through
    organized sub-clients for different resource types.

    Attributes:
        search: Client for web search.
        media: Client for image, news, and video search.
        reference: Client for autocomplete, instant answers, and regions.

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
        ```

    Note:
        This client is not instantiated directly. Instead, access it through
        the `duckduckgo` property of the main `ScrapeBadger` client.
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize DuckDuckGo client with all sub-clients.

        Args:
            client: The base HTTP client for making API requests.
        """
        self._client = client

        # Initialize sub-clients
        self._search = SearchClient(client)
        self._media = MediaClient(client)
        self._reference = ReferenceClient(client)

    @property
    def search(self) -> SearchClient:
        """Access the web search endpoint.

        Returns:
            SearchClient for DuckDuckGo web search.

        Example:
            ```python
            results = await client.duckduckgo.search.search("python asyncio")
            ```
        """
        return self._search

    @property
    def media(self) -> MediaClient:
        """Access the image, news, and video search endpoints.

        Returns:
            MediaClient for image, news, and video search.

        Example:
            ```python
            images = await client.duckduckgo.media.images("golden retriever")
            news = await client.duckduckgo.media.news("elections")
            videos = await client.duckduckgo.media.videos("guitar tutorial")
            ```
        """
        return self._media

    @property
    def reference(self) -> ReferenceClient:
        """Access autocomplete, instant answer, and region endpoints.

        Returns:
            ReferenceClient for autocomplete, instant answers, and regions.

        Example:
            ```python
            suggestions = await client.duckduckgo.reference.autocomplete("pyth")
            answer = await client.duckduckgo.reference.instant("pi")
            regions = await client.duckduckgo.reference.regions()
            ```
        """
        return self._reference
