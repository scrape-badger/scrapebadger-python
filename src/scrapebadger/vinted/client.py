"""Vinted API client combining all sub-clients.

This module provides the main VintedClient class that serves as the
entry point for all Vinted API operations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from scrapebadger.vinted.items import ItemsClient
from scrapebadger.vinted.reference import ReferenceClient
from scrapebadger.vinted.search import SearchClient
from scrapebadger.vinted.users import UsersClient

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class VintedClient:
    """Client for all Vinted API operations.

    This class provides access to all Vinted scraping endpoints through
    organized sub-clients for different resource types.

    Attributes:
        search: Client for searching Vinted items.
        items: Client for fetching item details.
        users: Client for user profiles and their items.
        reference: Client for reference data (brands, colors, statuses, markets).

    Example:
        ```python
        from scrapebadger import ScrapeBadger

        async with ScrapeBadger(api_key="your-key") as client:
            # Search for items
            results = await client.vinted.search.search("nike air max", market="fr")
            for item in results.items:
                print(f"{item.title}: {item.price.amount} {item.price.currency_code}")

            # Get item details
            detail = await client.vinted.items.get(123456789)
            print(f"Description: {detail.item.description}")

            # Get user profile
            profile = await client.vinted.users.get_profile(12345)
            print(f"{profile.user.login}: {profile.user.item_count} items")

            # Get available markets
            markets = await client.vinted.reference.markets()
            for m in markets.markets:
                print(f"{m.code}: {m.name}")
        ```

    Note:
        This client is not instantiated directly. Instead, access it through
        the `vinted` property of the main `ScrapeBadger` client.
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize Vinted client with all sub-clients.

        Args:
            client: The base HTTP client for making API requests.
        """
        self._client = client

        # Initialize sub-clients
        self._search = SearchClient(client)
        self._items = ItemsClient(client)
        self._users = UsersClient(client)
        self._reference = ReferenceClient(client)

    @property
    def search(self) -> SearchClient:
        """Access item search endpoints.

        Returns:
            SearchClient for searching Vinted items with filters.

        Example:
            ```python
            results = await client.vinted.search.search(
                "vintage jacket",
                market="de",
                price_from="20",
                price_to="100",
            )
            ```
        """
        return self._search

    @property
    def items(self) -> ItemsClient:
        """Access item detail endpoints.

        Returns:
            ItemsClient for fetching detailed item information.

        Example:
            ```python
            detail = await client.vinted.items.get(123456789)
            print(f"{detail.item.title}: {detail.item.description}")
            ```
        """
        return self._items

    @property
    def users(self) -> UsersClient:
        """Access user-related endpoints.

        Returns:
            UsersClient for fetching user profiles and their items.

        Example:
            ```python
            profile = await client.vinted.users.get_profile(12345)
            items = await client.vinted.users.get_items(12345)
            ```
        """
        return self._users

    @property
    def reference(self) -> ReferenceClient:
        """Access reference data endpoints.

        Returns:
            ReferenceClient for fetching brands, colors, statuses, and markets.

        Example:
            ```python
            markets = await client.vinted.reference.markets()
            brands = await client.vinted.reference.brands("nike")
            colors = await client.vinted.reference.colors(market="fr")
            statuses = await client.vinted.reference.statuses(market="fr")
            ```
        """
        return self._reference
