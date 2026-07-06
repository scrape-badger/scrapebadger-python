"""Leboncoin API client combining all sub-clients.

This module provides the main LeboncoinClient class that serves as the
entry point for all Leboncoin API operations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from scrapebadger.leboncoin.ads import AdsClient
from scrapebadger.leboncoin.reference import ReferenceClient
from scrapebadger.leboncoin.search import SearchClient
from scrapebadger.leboncoin.sellers import SellersClient

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class LeboncoinClient:
    """Client for all Leboncoin API operations.

    This class provides access to all Leboncoin scraping endpoints through
    organized sub-clients for different resource types.

    Attributes:
        search: Client for classified-ad search.
        ads: Client for ad detail and similar ads.
        sellers: Client for seller profile and listings.
        reference: Client for reference data (categories, regions, departments,
            locations, markets).

    Example:
        ```python
        from scrapebadger import ScrapeBadger

        async with ScrapeBadger(api_key="your-key") as client:
            # Search for ads
            results = await client.leboncoin.search.search("velo")
            for ad in results.ads:
                print(f"{ad.subject}: {ad.price_eur}")

            # Get ad detail
            detail = await client.leboncoin.ads.get_ad(2812345678)
            print(detail.ad.subject)

            # Get a seller profile
            seller = await client.leboncoin.sellers.get_seller("12345678")

            # Get reference regions
            regions = await client.leboncoin.reference.list_regions()
        ```

    Note:
        This client is not instantiated directly. Instead, access it through
        the `leboncoin` property of the main `ScrapeBadger` client.
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize Leboncoin client with all sub-clients.

        Args:
            client: The base HTTP client for making API requests.
        """
        self._client = client

        # Initialize sub-clients
        self._search = SearchClient(client)
        self._ads = AdsClient(client)
        self._sellers = SellersClient(client)
        self._reference = ReferenceClient(client)

    @property
    def search(self) -> SearchClient:
        """Access the classified-ad search endpoint.

        Returns:
            SearchClient for keyword/filter search.

        Example:
            ```python
            results = await client.leboncoin.search.search("velo", region_id="12")
            ```
        """
        return self._search

    @property
    def ads(self) -> AdsClient:
        """Access ad detail and similar-ad endpoints.

        Returns:
            AdsClient for fetching ad detail and similar ads.

        Example:
            ```python
            detail = await client.leboncoin.ads.get_ad(2812345678)
            similar = await client.leboncoin.ads.get_similar(2812345678)
            ```
        """
        return self._ads

    @property
    def sellers(self) -> SellersClient:
        """Access seller profile and listings endpoints.

        Returns:
            SellersClient for seller endpoints.

        Example:
            ```python
            profile = await client.leboncoin.sellers.get_seller("12345678")
            listings = await client.leboncoin.sellers.get_seller_listings("12345678")
            ```
        """
        return self._sellers

    @property
    def reference(self) -> ReferenceClient:
        """Access reference data endpoints.

        Returns:
            ReferenceClient for categories, regions, departments, locations, markets.

        Example:
            ```python
            categories = await client.leboncoin.reference.list_categories()
            regions = await client.leboncoin.reference.list_regions()
            markets = await client.leboncoin.reference.list_markets()
            ```
        """
        return self._reference
