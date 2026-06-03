"""Amazon API client combining all sub-clients.

This module provides the main AmazonClient class that serves as the
entry point for all Amazon API operations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from scrapebadger.amazon.listings import ListingsClient
from scrapebadger.amazon.products import ProductsClient
from scrapebadger.amazon.reference import ReferenceClient
from scrapebadger.amazon.search import SearchClient
from scrapebadger.amazon.sellers import SellersClient

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class AmazonClient:
    """Client for all Amazon API operations.

    This class provides access to all Amazon scraping endpoints through
    organized sub-clients for different resource types.

    Attributes:
        search: Client for keyword search and autocomplete.
        products: Client for product detail, offers, and reviews.
        listings: Client for bestsellers, new releases, deals, and category browse.
        sellers: Client for seller profile, storefront products, and feedback.
        reference: Client for reference data (markets, categories).

    Example:
        ```python
        from scrapebadger import ScrapeBadger

        async with ScrapeBadger(api_key="your-key") as client:
            # Search for products
            results = await client.amazon.search.search("wireless headphones")
            for item in results.results:
                print(f"{item.position}. {item.title}")

            # Get product detail
            detail = await client.amazon.products.get("B08N5WRWNW")
            print(detail.product.title)

            # Get bestsellers
            top = await client.amazon.listings.bestsellers(category="electronics")

            # Get a seller profile
            seller = await client.amazon.sellers.get("A2L77EE7U53NWQ")

            # Get supported markets
            markets = await client.amazon.reference.markets()
        ```

    Note:
        This client is not instantiated directly. Instead, access it through
        the `amazon` property of the main `ScrapeBadger` client.
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize Amazon client with all sub-clients.

        Args:
            client: The base HTTP client for making API requests.
        """
        self._client = client

        # Initialize sub-clients
        self._search = SearchClient(client)
        self._products = ProductsClient(client)
        self._listings = ListingsClient(client)
        self._sellers = SellersClient(client)
        self._reference = ReferenceClient(client)

    @property
    def search(self) -> SearchClient:
        """Access search and autocomplete endpoints.

        Returns:
            SearchClient for keyword search and autocomplete.

        Example:
            ```python
            results = await client.amazon.search.search("laptop", domain="de")
            suggestions = await client.amazon.search.autocomplete("lapt")
            ```
        """
        return self._search

    @property
    def products(self) -> ProductsClient:
        """Access product detail, offers, and reviews endpoints.

        Returns:
            ProductsClient for fetching product detail, offers, and reviews.

        Example:
            ```python
            detail = await client.amazon.products.get("B08N5WRWNW")
            offers = await client.amazon.products.offers("B08N5WRWNW")
            reviews = await client.amazon.products.reviews("B08N5WRWNW")
            ```
        """
        return self._products

    @property
    def listings(self) -> ListingsClient:
        """Access bestsellers, new releases, deals, and category browse endpoints.

        Returns:
            ListingsClient for listing endpoints.

        Example:
            ```python
            top = await client.amazon.listings.bestsellers(category="toys")
            new = await client.amazon.listings.new_releases(category="books")
            deals = await client.amazon.listings.deals()
            cat = await client.amazon.listings.category("172282")
            ```
        """
        return self._listings

    @property
    def sellers(self) -> SellersClient:
        """Access seller profile, products, and feedback endpoints.

        Returns:
            SellersClient for seller endpoints.

        Example:
            ```python
            profile = await client.amazon.sellers.get("A2L77EE7U53NWQ")
            products = await client.amazon.sellers.products("A2L77EE7U53NWQ")
            feedback = await client.amazon.sellers.feedback("A2L77EE7U53NWQ")
            ```
        """
        return self._sellers

    @property
    def reference(self) -> ReferenceClient:
        """Access reference data endpoints.

        Returns:
            ReferenceClient for fetching markets and categories.

        Example:
            ```python
            markets = await client.amazon.reference.markets()
            categories = await client.amazon.reference.categories()
            ```
        """
        return self._reference
