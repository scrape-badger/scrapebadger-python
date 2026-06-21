"""eBay Reference Data API client.

Provides methods for fetching the static marketplace and category lists.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from scrapebadger.ebay.models import CategoriesResponse, MarketsResponse

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class ReferenceClient:
    """Client for eBay reference data endpoints (markets, categories).

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            markets = await client.ebay.reference.list_markets()
            for m in markets.markets:
                print(f"{m.code}: {m.domain} ({m.currency})")

            categories = await client.ebay.reference.list_categories()
            for c in categories.categories:
                print(f"{c.name} -> {c.category_id}")
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize reference client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def list_markets(self) -> MarketsResponse:
        """Get all supported eBay marketplaces.

        Returns:
            Markets response with all supported marketplaces.

        Example:
            ```python
            result = await client.ebay.reference.list_markets()
            for m in result.markets:
                print(f"{m.code}: {m.name} ({m.domain})")
            ```
        """
        response = await self._client.get("/v1/ebay/markets")
        return MarketsResponse.model_validate(response)

    async def list_categories(self) -> CategoriesResponse:
        """Get eBay's reference category aliases.

        Returns:
            Categories response with all category aliases.

        Example:
            ```python
            result = await client.ebay.reference.list_categories()
            for c in result.categories:
                print(f"{c.name}: {c.category_id}")
            ```
        """
        response = await self._client.get("/v1/ebay/categories")
        return CategoriesResponse.model_validate(response)
