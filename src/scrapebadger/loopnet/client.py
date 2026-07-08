"""LoopNet API client combining all sub-clients.

This module provides the main LoopNetClient class that serves as the
entry point for all LoopNet API operations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from scrapebadger.loopnet.brokers import BrokersClient
from scrapebadger.loopnet.listings import ListingsClient
from scrapebadger.loopnet.reference import ReferenceClient
from scrapebadger.loopnet.search import SearchClient

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class LoopNetClient:
    """Client for all LoopNet API operations.

    This class provides access to all LoopNet commercial-real-estate scraping
    endpoints through organized sub-clients for different resource types.

    Attributes:
        search: Client for listing search (for-lease / for-sale / auctions).
        listings: Client for listing detail (by listing id).
        brokers: Client for broker profile + listings.
        reference: Client for reference data (markets, property types).

    Example:
        ```python
        from scrapebadger import ScrapeBadger

        async with ScrapeBadger(api_key="your-key") as client:
            # Search listings
            results = await client.loopnet.search.search("Houston, TX")
            for card in results.results:
                print(f"{card.position}. {card.address}")

            # Get listing detail
            detail = await client.loopnet.listings.get("12345678")
            print(detail.listing.price_text)

            # Get a broker profile
            broker = await client.loopnet.brokers.get("jane-doe", "w7x123")

            # Reference data
            markets = await client.loopnet.reference.markets()
        ```

    Note:
        This client is not instantiated directly. Instead, access it through
        the `loopnet` property of the main `ScrapeBadger` client.
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize LoopNet client with all sub-clients.

        Args:
            client: The base HTTP client for making API requests.
        """
        self._client = client

        # Initialize sub-clients
        self._search = SearchClient(client)
        self._listings = ListingsClient(client)
        self._brokers = BrokersClient(client)
        self._reference = ReferenceClient(client)

    @property
    def search(self) -> SearchClient:
        """Access the listing search endpoint.

        Returns:
            SearchClient for for-lease / for-sale / auction listing search.

        Example:
            ```python
            results = await client.loopnet.search.search("Houston, TX")
            ```
        """
        return self._search

    @property
    def listings(self) -> ListingsClient:
        """Access the listing detail endpoint.

        Returns:
            ListingsClient for fetching a listing by its id.

        Example:
            ```python
            detail = await client.loopnet.listings.get("12345678")
            ```
        """
        return self._listings

    @property
    def brokers(self) -> BrokersClient:
        """Access the broker profile endpoint.

        Returns:
            BrokersClient for fetching a broker's profile and listings.

        Example:
            ```python
            profile = await client.loopnet.brokers.get("jane-doe", "w7x123")
            ```
        """
        return self._brokers

    @property
    def reference(self) -> ReferenceClient:
        """Access reference data endpoints.

        Returns:
            ReferenceClient for coverage markets and property types.

        Example:
            ```python
            markets = await client.loopnet.reference.markets()
            types = await client.loopnet.reference.property_types()
            ```
        """
        return self._reference
