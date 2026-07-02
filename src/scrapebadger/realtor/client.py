"""Realtor API client combining all sub-clients.

This module provides the main RealtorClient class that serves as the
entry point for all Realtor API operations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from scrapebadger.realtor.properties import PropertiesClient
from scrapebadger.realtor.reference import ReferenceClient
from scrapebadger.realtor.search import SearchClient

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class RealtorClient:
    """Client for all Realtor API operations.

    This class provides access to all Realtor scraping endpoints through
    organized sub-clients for different resource types. It unifies realtor.com
    (US) and realtor.ca (Canada) behind a single ``market`` parameter.

    Attributes:
        search: Client for property search and location autocomplete.
        properties: Client for single-property detail.
        reference: Client for reference data (markets).

    Example:
        ```python
        from scrapebadger import ScrapeBadger

        async with ScrapeBadger(api_key="your-key") as client:
            # Search for listings
            results = await client.realtor.search.search("Austin, TX")
            for prop in results.results:
                print(prop.property_id, prop.list_price)

            # Get property detail
            detail = await client.realtor.properties.get_property("1234567890")
            print(detail.beds, detail.baths, detail.sqft)

            # Location autocomplete
            hits = await client.realtor.search.autocomplete("toronto", market="ca")

            # Get supported markets
            markets = await client.realtor.reference.list_markets()
        ```

    Note:
        This client is not instantiated directly. Instead, access it through
        the `realtor` property of the main `ScrapeBadger` client.
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize Realtor client with all sub-clients.

        Args:
            client: The base HTTP client for making API requests.
        """
        self._client = client

        # Initialize sub-clients
        self._search = SearchClient(client)
        self._properties = PropertiesClient(client)
        self._reference = ReferenceClient(client)

    @property
    def search(self) -> SearchClient:
        """Access property search and autocomplete endpoints.

        Returns:
            SearchClient for property search and location autocomplete.

        Example:
            ```python
            results = await client.realtor.search.search("Miami, FL")
            hits = await client.realtor.search.autocomplete("miami")
            ```
        """
        return self._search

    @property
    def properties(self) -> PropertiesClient:
        """Access the single-property detail endpoint.

        Returns:
            PropertiesClient for fetching full property detail.

        Example:
            ```python
            detail = await client.realtor.properties.get_property("1234567890")
            ```
        """
        return self._properties

    @property
    def reference(self) -> ReferenceClient:
        """Access reference data endpoints.

        Returns:
            ReferenceClient for fetching supported markets.

        Example:
            ```python
            markets = await client.realtor.reference.list_markets()
            ```
        """
        return self._reference
