"""Vinted Search API client.

Provides methods for searching Vinted items.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.vinted.models import SearchResponse

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class SearchClient:
    """Client for Vinted search endpoints.

    Provides async methods for searching items on Vinted marketplaces.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            # Search for items
            results = await client.vinted.search.search("nike air max")
            for item in results.items:
                print(f"{item.title}: {item.price.amount} {item.price.currency_code}")

            # Search with filters
            results = await client.vinted.search.search(
                "nike",
                market="fr",
                price_from="10",
                price_to="50",
                per_page=40,
            )
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize search client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def search(
        self,
        query: str,
        *,
        market: str = "fr",
        page: int = 1,
        per_page: int = 20,
        price_from: str | None = None,
        price_to: str | None = None,
        brand_ids: str | None = None,
        color_ids: str | None = None,
        status_ids: str | None = None,
        order: str | None = None,
    ) -> SearchResponse:
        """Search for items on Vinted.

        Args:
            query: Search query string.
            market: Vinted market code (e.g. "fr", "de", "uk"). Defaults to "fr".
            page: Page number (1-indexed). Defaults to 1.
            per_page: Number of items per page (max varies by market). Defaults to 20.
            price_from: Minimum price filter.
            price_to: Maximum price filter.
            brand_ids: Comma-separated brand IDs to filter by.
            color_ids: Comma-separated color IDs to filter by.
            status_ids: Comma-separated status IDs to filter by.
            order: Sort order (e.g. "newest_first", "price_low_to_high").

        Returns:
            Search response with matching items and pagination metadata.

        Raises:
            AuthenticationError: If the API key is invalid.
            ValidationError: If the parameters are invalid.

        Example:
            ```python
            results = await client.vinted.search.search(
                "vintage jacket",
                market="de",
                price_from="20",
                price_to="100",
                order="newest_first",
            )
            print(f"Found {results.pagination.total_entries} items")
            for item in results.items:
                print(f"  {item.title} - {item.price.amount} {item.price.currency_code}")
            ```
        """
        params: dict[str, Any] = {
            "query": query,
            "market": market,
            "page": page,
            "per_page": per_page,
            "price_from": price_from,
            "price_to": price_to,
            "brand_ids": brand_ids,
            "color_ids": color_ids,
            "status_ids": status_ids,
            "order": order,
        }
        response = await self._client.get("/v1/vinted/search", params=params)
        return SearchResponse.model_validate(response)
