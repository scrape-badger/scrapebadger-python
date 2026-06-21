"""eBay Categories API client.

Provides a method for browsing the active listings within a category.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.ebay.models import CategoryResponse

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class CategoriesClient:
    """Client for the eBay category browse endpoint.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            result = await client.ebay.categories.browse_category("9355")
            for it in result.results:
                print(it.title)
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize categories client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def browse_category(
        self,
        category_id: str,
        *,
        domain: str = "com",
        page: int = 1,
        per_page: int | None = None,
        sort_by: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
    ) -> CategoryResponse:
        """List active listings within an eBay category.

        Args:
            category_id: The eBay category id (required).
            domain: eBay marketplace domain (e.g. "com", "de"). Defaults to "com".
            page: Page number (1-indexed). Defaults to 1.
            per_page: Results per page (60, 120 or 240; clamped).
            sort_by: Sort order ("best_match", "ending_soonest", "newly_listed",
                "price_low_to_high", "price_high_to_low").
            min_price: Minimum price filter.
            max_price: Maximum price filter.

        Returns:
            Category response with result cards, facets, and pagination.

        Example:
            ```python
            result = await client.ebay.categories.browse_category("9355", domain="com")
            for it in result.results:
                print(it.title)
            ```
        """
        params: dict[str, Any] = {
            "domain": domain,
            "page": page,
            "per_page": per_page,
            "sort_by": sort_by,
            "min_price": min_price,
            "max_price": max_price,
        }
        response = await self._client.get(
            f"/v1/ebay/categories/{category_id}/items", params=params
        )
        return CategoryResponse.model_validate(response)
