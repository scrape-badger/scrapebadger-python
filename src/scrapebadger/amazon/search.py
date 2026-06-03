"""Amazon Search API client.

Provides methods for keyword search and keyword autocomplete suggestions.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.amazon.models import AutocompleteResponse, SearchResponse

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class SearchClient:
    """Client for Amazon search and autocomplete endpoints.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            results = await client.amazon.search.search("wireless headphones")
            for item in results.results:
                print(f"{item.position}. {item.title}")

            suggestions = await client.amazon.search.autocomplete("lapt")
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
        page: int = 1,
        sort_by: str | None = None,
        category: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        zip: str | None = None,
        language: str | None = None,
    ) -> SearchResponse:
        """Search Amazon for products by keyword.

        Args:
            query: Search query string.
            domain: Amazon marketplace domain (e.g. "com", "co.uk", "de"). Defaults to "com".
            page: Page number (1-indexed). Defaults to 1.
            sort_by: Sort order (e.g. "price_low_to_high", "featured", "review_rank").
            category: Category / department alias to scope the search.
            min_price: Minimum price filter.
            max_price: Maximum price filter.
            zip: Delivery ZIP / postal code for localized price & availability.
            language: Preferred content language / locale (e.g. "en_US").

        Returns:
            Search response with matching results and pagination metadata.

        Raises:
            AuthenticationError: If the API key is invalid.
            ValidationError: If the parameters are invalid.

        Example:
            ```python
            results = await client.amazon.search.search(
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
            "page": page,
            "sort_by": sort_by,
            "category": category,
            "min_price": min_price,
            "max_price": max_price,
            "zip": zip,
            "language": language,
        }
        response = await self._client.get("/v1/amazon/search", params=params)
        return SearchResponse.model_validate(response)

    async def autocomplete(
        self,
        query: str,
        *,
        domain: str = "com",
    ) -> AutocompleteResponse:
        """Get Amazon keyword autocomplete suggestions.

        Args:
            query: Partial search query string.
            domain: Amazon marketplace domain (e.g. "com", "de"). Defaults to "com".

        Returns:
            Autocomplete response with keyword suggestions.

        Example:
            ```python
            result = await client.amazon.search.autocomplete("blue")
            for s in result.suggestions:
                print(s.value)
            ```
        """
        params: dict[str, Any] = {"query": query, "domain": domain}
        response = await self._client.get("/v1/amazon/autocomplete", params=params)
        return AutocompleteResponse.model_validate(response)
