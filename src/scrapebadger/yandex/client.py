"""Yandex API client combining all sub-clients.

This module provides the main YandexClient class that serves as the
entry point for all Yandex API operations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from scrapebadger.yandex.images import ImagesClient
from scrapebadger.yandex.reference import ReferenceClient
from scrapebadger.yandex.search import SearchClient

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class YandexClient:
    """Client for all Yandex API operations.

    This class provides access to all Yandex scraping endpoints through
    organized sub-clients for different resource types.

    Attributes:
        search: Client for web search.
        images: Client for image search and reverse-image (CBIR) search.
        reference: Client for the supported-markets list.

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

    Note:
        This client is not instantiated directly. Instead, access it through
        the `yandex` property of the main `ScrapeBadger` client.
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize Yandex client with all sub-clients.

        Args:
            client: The base HTTP client for making API requests.
        """
        self._client = client

        # Initialize sub-clients
        self._search = SearchClient(client)
        self._images = ImagesClient(client)
        self._reference = ReferenceClient(client)

    @property
    def search(self) -> SearchClient:
        """Access the web search endpoint.

        Returns:
            SearchClient for Yandex web search.

        Example:
            ```python
            results = await client.yandex.search.search("python asyncio")
            ```
        """
        return self._search

    @property
    def images(self) -> ImagesClient:
        """Access the image search and reverse-image endpoints.

        Returns:
            ImagesClient for image search and reverse-image (CBIR) search.

        Example:
            ```python
            images = await client.yandex.images.search("golden retriever")
            reverse = await client.yandex.images.reverse(
                "https://example.com/photo.jpg"
            )
            ```
        """
        return self._images

    @property
    def reference(self) -> ReferenceClient:
        """Access the supported-markets endpoint.

        Returns:
            ReferenceClient for the list of supported Yandex markets.

        Example:
            ```python
            markets = await client.yandex.reference.markets()
            ```
        """
        return self._reference
