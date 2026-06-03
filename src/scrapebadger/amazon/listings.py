"""Amazon Listings API client.

Provides methods for bestsellers, new releases, deals, and category browse.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.amazon.models import (
    BestsellersResponse,
    CategoryResponse,
    DealsResponse,
    NewReleasesResponse,
)

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class ListingsClient:
    """Client for Amazon listing endpoints (bestsellers, new releases, deals, category).

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            top = await client.amazon.listings.bestsellers(category="electronics")
            for item in top.bestsellers:
                print(f"#{item.rank}: {item.title}")
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize listings client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def bestsellers(
        self,
        *,
        domain: str = "com",
        category: str | None = None,
        page: int = 1,
    ) -> BestsellersResponse:
        """Get the bestsellers list for a marketplace / category.

        Args:
            domain: Amazon marketplace domain (e.g. "com", "de"). Defaults to "com".
            category: Bestsellers node / category alias.
            page: Page number (1-indexed). Defaults to 1.

        Returns:
            Bestsellers response with ranked products and pagination.

        Example:
            ```python
            result = await client.amazon.listings.bestsellers(category="toys")
            for b in result.bestsellers:
                print(f"#{b.rank}: {b.title}")
            ```
        """
        params: dict[str, Any] = {"domain": domain, "category": category, "page": page}
        response = await self._client.get("/v1/amazon/bestsellers", params=params)
        return BestsellersResponse.model_validate(response)

    async def new_releases(
        self,
        *,
        domain: str = "com",
        category: str | None = None,
        page: int = 1,
    ) -> NewReleasesResponse:
        """Get the new-releases list for a marketplace / category.

        Args:
            domain: Amazon marketplace domain (e.g. "com", "de"). Defaults to "com".
            category: New-releases node / category alias.
            page: Page number (1-indexed). Defaults to 1.

        Returns:
            New-releases response with ranked products and pagination.

        Example:
            ```python
            result = await client.amazon.listings.new_releases(category="books")
            for nr in result.new_releases:
                print(f"#{nr.rank}: {nr.title}")
            ```
        """
        params: dict[str, Any] = {"domain": domain, "category": category, "page": page}
        response = await self._client.get("/v1/amazon/new-releases", params=params)
        return NewReleasesResponse.model_validate(response)

    async def deals(
        self,
        *,
        domain: str = "com",
        category: str | None = None,
        page: int = 1,
    ) -> DealsResponse:
        """Get current deals for a marketplace / category.

        Args:
            domain: Amazon marketplace domain (e.g. "com", "de"). Defaults to "com".
            category: Deals category filter.
            page: Page number (1-indexed). Defaults to 1.

        Returns:
            Deals response with deal rows and pagination.

        Example:
            ```python
            result = await client.amazon.listings.deals()
            for d in result.deals:
                print(f"{d.title}: -{d.discount_percent}%")
            ```
        """
        params: dict[str, Any] = {"domain": domain, "category": category, "page": page}
        response = await self._client.get("/v1/amazon/deals", params=params)
        return DealsResponse.model_validate(response)

    async def category(
        self,
        node: str,
        *,
        domain: str = "com",
        page: int = 1,
        sort_by: str | None = None,
    ) -> CategoryResponse:
        """Browse a category / department by browse-node ID.

        Args:
            node: The browse-node ID (required).
            domain: Amazon marketplace domain (e.g. "com", "de"). Defaults to "com".
            page: Page number (1-indexed). Defaults to 1.
            sort_by: Sort order (e.g. "price_low_to_high", "featured").

        Returns:
            Category response with result rows and pagination.

        Example:
            ```python
            result = await client.amazon.listings.category("172282", domain="com")
            for r in result.results:
                print(r.title)
            ```
        """
        params: dict[str, Any] = {
            "node": node,
            "domain": domain,
            "page": page,
            "sort_by": sort_by,
        }
        response = await self._client.get("/v1/amazon/category", params=params)
        return CategoryResponse.model_validate(response)
