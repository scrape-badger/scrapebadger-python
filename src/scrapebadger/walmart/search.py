"""Walmart Search API client.

Keyword search, category browse, the deals feed, and search-box autocomplete.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.walmart.models import AutocompleteResponse, SearchResponse

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class SearchClient:
    """Client for Walmart search, category, deals, and autocomplete endpoints.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            results = await client.walmart.search.search("laptop", sort="price_low")
            for item in results.items:
                print(f"{item.position}. {item.name} — ${item.price}")

            deals = await client.walmart.search.deals()
            suggestions = await client.walmart.search.autocomplete("lapt")
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
        page: int = 1,
        sort: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        facet: str | None = None,
    ) -> SearchResponse:
        """Search walmart.com.

        Args:
            query: Search keywords, e.g. ``"laptop"``.
            page: Page number, 1-10. Results dry up after page 10 regardless of
                the total Walmart reports.
            sort: Result ordering — ``"best_match"``, ``"best_seller"``,
                ``"price_low"``, ``"price_high"``, ``"rating_high"``, ``"new"``.
            min_price: Minimum price in USD.
            max_price: Maximum price in USD.
            facet: Walmart facet filter, e.g. ``"brand:HP"``. Facets can be
                APPLIED but not enumerated — Walmart renders the filter rail
                client-side.

        Returns:
            SearchResponse with ~40-60 organic products per page. Sponsored ad
            tiles are dropped; sponsored *products* are flagged ``is_sponsored``.

        Raises:
            AuthenticationError: If the API key is invalid.
            ValidationError: If the parameters are invalid.

        Example:
            ```python
            results = await client.walmart.search.search(
                "running shoes", min_price=20, max_price=100, sort="price_low"
            )
            print(results.total_results_reported, results.max_page)
            ```
        """
        params: dict[str, Any] = {
            "query": query,
            "page": page,
            "sort": sort,
            "min_price": min_price,
            "max_price": max_price,
            "facet": facet,
        }
        response = await self._client.get("/v1/walmart/search", params=params)
        return SearchResponse.model_validate(response)

    async def category(
        self,
        path: str,
        *,
        page: int = 1,
        min_price: float | None = None,
        max_price: float | None = None,
        facet: str | None = None,
    ) -> SearchResponse:
        """Browse a Walmart category. Same result shape as :meth:`search`.

        Args:
            path: Walmart browse path, e.g. ``"electronics/3944"`` (from a
                ``walmart.com/browse/...`` URL), or a ``/cp/...`` department path.
            page: Page number, 1-11.
            min_price: Minimum price in USD.
            max_price: Maximum price in USD.
            facet: Facet filter, e.g. ``"brand:HP"``.

        Returns:
            SearchResponse with the category's product cards.

        Note:
            No ``sort`` parameter — Walmart's browse pages ignore it. Sort on
            :meth:`search` instead.

        Example:
            ```python
            page1 = await client.walmart.search.category("electronics/3944")
            ```
        """
        params: dict[str, Any] = {
            "path": path,
            "page": page,
            "min_price": min_price,
            "max_price": max_price,
            "facet": facet,
        }
        response = await self._client.get("/v1/walmart/category", params=params)
        return SearchResponse.model_validate(response)

    async def deals(
        self,
        *,
        page: int = 1,
        min_price: float | None = None,
        max_price: float | None = None,
    ) -> SearchResponse:
        """Walmart's current deals, rollbacks and clearance.

        Args:
            page: Page number, 1-11.
            min_price: Minimum price in USD.
            max_price: Maximum price in USD.

        Returns:
            SearchResponse with the deals feed's product cards.

        Example:
            ```python
            result = await client.walmart.search.deals(max_price=50)
            for item in result.items:
                print(item.name, item.price, item.was_price)
            ```
        """
        params: dict[str, Any] = {
            "page": page,
            "min_price": min_price,
            "max_price": max_price,
        }
        response = await self._client.get("/v1/walmart/deals", params=params)
        return SearchResponse.model_validate(response)

    async def autocomplete(self, query: str) -> AutocompleteResponse:
        """Walmart search-box suggestions.

        Args:
            query: Partial search term, e.g. ``"lapt"``.

        Returns:
            AutocompleteResponse with keyword and department suggestions.

        Example:
            ```python
            result = await client.walmart.search.autocomplete("lapt")
            for s in result.suggestions:
                print(s.query, s.department_name)
            ```
        """
        params: dict[str, Any] = {"query": query}
        response = await self._client.get("/v1/walmart/autocomplete", params=params)
        return AutocompleteResponse.model_validate(response)
