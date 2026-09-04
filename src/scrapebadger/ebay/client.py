"""eBay API client combining all sub-clients.

This module provides the main EbayClient class that serves as the
entry point for all eBay API operations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from scrapebadger.ebay.categories import CategoriesClient
from scrapebadger.ebay.items import ItemsClient
from scrapebadger.ebay.reference import ReferenceClient
from scrapebadger.ebay.search import SearchClient
from scrapebadger.ebay.sellers import SellersClient

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class EbayClient:
    """Client for all eBay API operations.

    This class provides access to all eBay scraping endpoints through
    organized sub-clients for different resource types.

    Attributes:
        search: Client for active/visual/completed search and autocomplete.
        items: Client for item detail and item reviews.
        sellers: Client for seller profile, items, and feedback.
        categories: Client for category browse.
        reference: Client for reference data (markets, categories).

    Example:
        ```python
        from scrapebadger import ScrapeBadger

        async with ScrapeBadger(api_key="your-key") as client:
            # Search for listings
            results = await client.ebay.search.search("nintendo switch")
            for item in results.results:
                print(f"{item.position}. {item.title}")

            # Get item detail
            detail = await client.ebay.items.get_item("123456789012")
            print(detail.item.title)

            # Get a seller profile
            seller = await client.ebay.sellers.get_seller("musicmagpie")

            # Get supported markets
            markets = await client.ebay.reference.list_markets()
        ```

    Note:
        This client is not instantiated directly. Instead, access it through
        the `ebay` property of the main `ScrapeBadger` client.
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize eBay client with all sub-clients.

        Args:
            client: The base HTTP client for making API requests.
        """
        self._client = client

        # Initialize sub-clients
        self._search = SearchClient(client)
        self._items = ItemsClient(client)
        self._sellers = SellersClient(client)
        self._categories = CategoriesClient(client)
        self._reference = ReferenceClient(client)

    @property
    def search(self) -> SearchClient:
        """Access search, completed-listing, and autocomplete endpoints.

        Returns:
            SearchClient for keyword search, completed/sold search, and autocomplete.

        Example:
            ```python
            results = await client.ebay.search.search("laptop", domain="de")
            sold = await client.ebay.search.completed("laptop")
            suggestions = await client.ebay.search.autocomplete("lapt")
            ```
        """
        return self._search

    @property
    def items(self) -> ItemsClient:
        """Access item detail and item review endpoints.

        Returns:
            ItemsClient for fetching item detail and item reviews.

        Example:
            ```python
            detail = await client.ebay.items.get_item("123456789012")
            reviews = await client.ebay.items.get_item_reviews("123456789012")
            ```
        """
        return self._items

    @property
    def sellers(self) -> SellersClient:
        """Access seller profile, items, and feedback endpoints.

        Returns:
            SellersClient for seller endpoints.

        Example:
            ```python
            profile = await client.ebay.sellers.get_seller("musicmagpie")
            items = await client.ebay.sellers.get_seller_items("musicmagpie")
            feedback = await client.ebay.sellers.get_seller_feedback("musicmagpie")
            ```
        """
        return self._sellers

    @property
    def categories(self) -> CategoriesClient:
        """Access the category browse endpoint.

        Returns:
            CategoriesClient for browsing listings within a category.

        Example:
            ```python
            result = await client.ebay.categories.browse_category("9355")
            for it in result.results:
                print(it.title)
            ```
        """
        return self._categories

    @property
    def reference(self) -> ReferenceClient:
        """Access reference data endpoints.

        Returns:
            ReferenceClient for fetching markets and categories.

        Example:
            ```python
            markets = await client.ebay.reference.list_markets()
            categories = await client.ebay.reference.list_categories()
            ```
        """
        return self._reference
