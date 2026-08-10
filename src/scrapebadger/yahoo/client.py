"""Yahoo API client combining all sub-clients.

This module provides the main YahooClient class that serves as the
entry point for all Yahoo API operations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from scrapebadger.yahoo.media import MediaClient
from scrapebadger.yahoo.news import NewsClient
from scrapebadger.yahoo.reference import ReferenceClient
from scrapebadger.yahoo.search import SearchClient

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class YahooClient:
    """Client for all Yahoo API operations.

    This class provides access to all Yahoo scraping endpoints through
    organized sub-clients for different resource types.

    Attributes:
        search: Client for web search and search-box autocomplete.
        media: Client for image search and video search.
        news: Client for the news vertical.
        reference: Client for reference data (markets).

    Example:
        ```python
        from scrapebadger import ScrapeBadger

        async with ScrapeBadger(api_key="your-key") as client:
            # Web search
            results = await client.yahoo.search.search("coffee machine")
            for r in results.results:
                print(f"{r.position}. {r.title} — {r.url}")

            # Images and videos
            images = await client.yahoo.media.images("cats")
            videos = await client.yahoo.media.videos("cats")

            # News
            news = await client.yahoo.news.news("ai")

            # Markets
            markets = await client.yahoo.reference.markets()
        ```

    Note:
        This client is not instantiated directly. Instead, access it through
        the `yahoo` property of the main `ScrapeBadger` client.
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize Yahoo client with all sub-clients.

        Args:
            client: The base HTTP client for making API requests.
        """
        self._client = client

        # Initialize sub-clients
        self._search = SearchClient(client)
        self._media = MediaClient(client)
        self._news = NewsClient(client)
        self._reference = ReferenceClient(client)

    @property
    def search(self) -> SearchClient:
        """Access web search and autocomplete endpoints.

        Returns:
            SearchClient for the web SERP and search-box autocomplete.

        Example:
            ```python
            results = await client.yahoo.search.search("laptop", market="de")
            suggestions = await client.yahoo.search.autocomplete("lapt")
            ```
        """
        return self._search

    @property
    def media(self) -> MediaClient:
        """Access image and video search endpoints.

        Returns:
            MediaClient for Yahoo image search and video search.

        Example:
            ```python
            images = await client.yahoo.media.images("cats")
            videos = await client.yahoo.media.videos("cats")
            ```
        """
        return self._media

    @property
    def news(self) -> NewsClient:
        """Access the news vertical endpoint.

        Returns:
            NewsClient for the Yahoo news vertical.

        Example:
            ```python
            news = await client.yahoo.news.news("ai")
            ```
        """
        return self._news

    @property
    def reference(self) -> ReferenceClient:
        """Access reference data endpoints.

        Returns:
            ReferenceClient for fetching the supported Yahoo markets.

        Example:
            ```python
            markets = await client.yahoo.reference.markets()
            ```
        """
        return self._reference
