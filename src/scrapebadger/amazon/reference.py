"""Amazon Reference Data API client.

Provides methods for fetching the static marketplace and category lists.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from scrapebadger.amazon.models import CategoriesResponse, MarketsResponse

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class ReferenceClient:
    """Client for Amazon reference data endpoints (markets, categories).

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            markets = await client.amazon.reference.markets()
            for m in markets.markets:
                print(f"{m.code}: {m.domain} ({m.currency})")

            categories = await client.amazon.reference.categories()
            for c in categories.categories:
                print(f"{c.name} -> {c.alias}")
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize reference client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def markets(self) -> MarketsResponse:
        """Get all supported Amazon marketplaces.

        Returns:
            Markets response with all supported marketplaces.

        Example:
            ```python
            result = await client.amazon.reference.markets()
            for m in result.markets:
                print(f"{m.code}: {m.name} ({m.domain})")
            ```
        """
        response = await self._client.get("/v1/amazon/markets")
        return MarketsResponse.model_validate(response)

    async def categories(self) -> CategoriesResponse:
        """Get the reference department / category aliases.

        Returns:
            Categories response with all category aliases.

        Example:
            ```python
            result = await client.amazon.reference.categories()
            for c in result.categories:
                print(f"{c.name}: {c.alias}")
            ```
        """
        response = await self._client.get("/v1/amazon/categories")
        return CategoriesResponse.model_validate(response)
