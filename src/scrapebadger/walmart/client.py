"""Walmart API client combining all sub-clients.

This module provides the main WalmartClient class that serves as the
entry point for all Walmart API operations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from scrapebadger.walmart.products import ProductsClient
from scrapebadger.walmart.reference import ReferenceClient
from scrapebadger.walmart.search import SearchClient
from scrapebadger.walmart.sellers import SellersClient
from scrapebadger.walmart.stores import StoresClient

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class WalmartClient:
    """Client for all Walmart API operations.

    This class provides access to all Walmart scraping endpoints through
    organized sub-clients for different resource types. Walmart is US-only —
    walmart.com is the single supported market, so no method takes a
    market/country parameter.

    Attributes:
        search: Client for search, category browse, deals, and autocomplete.
        products: Client for product detail and product reviews.
        sellers: Client for marketplace seller profile and catalogue.
        stores: Client for physical store detail.
        reference: Client for reference data (markets, health).

    Example:
        ```python
        from scrapebadger import ScrapeBadger

        async with ScrapeBadger(api_key="your-key") as client:
            # Search
            results = await client.walmart.search.search("laptop")
            for item in results.items:
                print(f"{item.position}. {item.name} — ${item.price}")

            # Product detail
            product = await client.walmart.products.get_product("5689919121")
            print(product.name, product.upc)

            # Seller profile
            seller = await client.walmart.sellers.get_seller("101040442")

            # Store detail
            store = await client.walmart.stores.get_store("100")
        ```

    Note:
        This client is not instantiated directly. Instead, access it through
        the `walmart` property of the main `ScrapeBadger` client.
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize Walmart client with all sub-clients.

        Args:
            client: The base HTTP client for making API requests.
        """
        self._client = client

        # Initialize sub-clients
        self._search = SearchClient(client)
        self._products = ProductsClient(client)
        self._sellers = SellersClient(client)
        self._stores = StoresClient(client)
        self._reference = ReferenceClient(client)

    @property
    def search(self) -> SearchClient:
        """Access search, category, deals, and autocomplete endpoints.

        Returns:
            SearchClient for keyword search, category browse, the deals feed,
            and search-box autocomplete.

        Example:
            ```python
            results = await client.walmart.search.search("laptop", sort="price_low")
            browse = await client.walmart.search.category("electronics/3944")
            deals = await client.walmart.search.deals()
            suggestions = await client.walmart.search.autocomplete("lapt")
            ```
        """
        return self._search

    @property
    def products(self) -> ProductsClient:
        """Access product detail and product review endpoints.

        Returns:
            ProductsClient for fetching product detail and reviews.

        Example:
            ```python
            product = await client.walmart.products.get_product("5689919121")
            reviews = await client.walmart.products.get_reviews("5689919121")
            ```
        """
        return self._products

    @property
    def sellers(self) -> SellersClient:
        """Access marketplace seller profile and catalogue endpoints.

        Returns:
            SellersClient for seller endpoints.

        Example:
            ```python
            profile = await client.walmart.sellers.get_seller("101040442")
            catalogue = await client.walmart.sellers.get_seller_products(
                "101040442", "laptop"
            )
            ```
        """
        return self._sellers

    @property
    def stores(self) -> StoresClient:
        """Access the physical store detail endpoint.

        Returns:
            StoresClient for store detail plus nearby stores.

        Example:
            ```python
            result = await client.walmart.stores.get_store("100")
            print(result.store.city, result.nearby_count)
            ```
        """
        return self._stores

    @property
    def reference(self) -> ReferenceClient:
        """Access reference data endpoints.

        Returns:
            ReferenceClient for fetching markets and the service health check.

        Example:
            ```python
            markets = await client.walmart.reference.list_markets()
            status = await client.walmart.reference.health()
            ```
        """
        return self._reference
