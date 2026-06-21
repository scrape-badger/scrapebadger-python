"""eBay Search API client.

Provides methods for active-listing search, completed/sold search, and
keyword autocomplete suggestions.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.ebay.models import AutocompleteResponse, SearchResponse

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class SearchClient:
    """Client for eBay search, completed-listing, and autocomplete endpoints.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            results = await client.ebay.search.search("nintendo switch")
            for item in results.results:
                print(f"{item.position}. {item.title}")

            sold = await client.ebay.search.completed("iphone 13")

            suggestions = await client.ebay.search.autocomplete("nint")
            for s in suggestions.suggestions:
                print(s.value)
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
        domain: str = "com",
        category_id: str | None = None,
        page: int = 1,
        per_page: int | None = None,
        sort_by: str | None = None,
        condition: str | None = None,
        buying_format: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        free_shipping: bool | None = None,
    ) -> SearchResponse:
        """Search an eBay marketplace for active listings.

        Args:
            query: Search keywords.
            domain: eBay marketplace domain (e.g. "com", "co.uk", "de"). Defaults to "com".
            category_id: Restrict the search to a category id.
            page: Page number (1-indexed). Defaults to 1.
            per_page: Results per page (60, 120 or 240; clamped).
            sort_by: Sort order ("best_match", "ending_soonest", "newly_listed",
                "price_low_to_high", "price_high_to_low").
            condition: Item condition ("new", "open_box", "refurbished", "used", "for_parts").
            buying_format: Buying format ("auction", "buy_it_now", "best_offer").
            min_price: Minimum price filter.
            max_price: Maximum price filter.
            free_shipping: Restrict to listings with free shipping.

        Returns:
            Search response with matching results, facets, and pagination metadata.

        Raises:
            AuthenticationError: If the API key is invalid.
            ValidationError: If the parameters are invalid.

        Example:
            ```python
            results = await client.ebay.search.search(
                "running shoes",
                domain="co.uk",
                min_price=20,
                max_price=100,
                sort_by="price_low_to_high",
            )
            print(f"Page {results.pagination.current_page}")
            ```
        """
        params: dict[str, Any] = {
            "query": query,
            "domain": domain,
            "category_id": category_id,
            "page": page,
            "per_page": per_page,
            "sort_by": sort_by,
            "condition": condition,
            "buying_format": buying_format,
            "min_price": min_price,
            "max_price": max_price,
            "free_shipping": free_shipping,
        }
        response = await self._client.get("/v1/ebay/search", params=params)
        return SearchResponse.model_validate(response)

    async def completed(
        self,
        query: str,
        *,
        domain: str = "com",
        category_id: str | None = None,
        page: int = 1,
        per_page: int | None = None,
        sort_by: str | None = None,
        condition: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
    ) -> SearchResponse:
        """Search completed/sold listings — eBay's sold-price history.

        Args:
            query: Search keywords.
            domain: eBay marketplace domain (e.g. "com", "co.uk", "de"). Defaults to "com".
            category_id: Restrict the search to a category id.
            page: Page number (1-indexed). Defaults to 1.
            per_page: Results per page (60, 120 or 240; clamped).
            sort_by: Sort order ("best_match", "ending_soonest", "newly_listed",
                "price_low_to_high", "price_high_to_low").
            condition: Item condition ("new", "open_box", "refurbished", "used", "for_parts").
            min_price: Minimum price filter.
            max_price: Maximum price filter.

        Returns:
            Search response with sold results (``sold=True``) and pagination metadata.

        Example:
            ```python
            sold = await client.ebay.search.completed("ipad pro", domain="com")
            for item in sold.results:
                print(f"{item.title}: {item.price.raw if item.price else 'N/A'}")
            ```
        """
        params: dict[str, Any] = {
            "query": query,
            "domain": domain,
            "category_id": category_id,
            "page": page,
            "per_page": per_page,
            "sort_by": sort_by,
            "condition": condition,
            "min_price": min_price,
            "max_price": max_price,
        }
        response = await self._client.get("/v1/ebay/completed", params=params)
        return SearchResponse.model_validate(response)

    async def autocomplete(
        self,
        query: str,
        *,
        domain: str = "com",
    ) -> AutocompleteResponse:
        """Get eBay keyword autocomplete suggestions.

        Args:
            query: Partial search query prefix.
            domain: eBay marketplace domain (e.g. "com", "de"). Defaults to "com".

        Returns:
            Autocomplete response with keyword suggestions.

        Example:
            ```python
            result = await client.ebay.search.autocomplete("nint")
            for s in result.suggestions:
                print(s.value)
            ```
        """
        params: dict[str, Any] = {"query": query, "domain": domain}
        response = await self._client.get("/v1/ebay/autocomplete", params=params)
        return AutocompleteResponse.model_validate(response)
