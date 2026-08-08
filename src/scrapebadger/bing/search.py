"""Bing Search API client.

Web search and search-box autocomplete.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from scrapebadger.bing.models import AutocompleteResponse, SearchResponse

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient

SafeSearch = Literal["off", "moderate", "strict"]


class SearchClient:
    """Client for Bing web search and autocomplete endpoints.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            results = await client.bing.search.search("coffee machine")
            for r in results.results:
                print(f"{r.position}. {r.title} — {r.url}")

            suggestions = await client.bing.search.autocomplete("coff")
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
        market: str = "en-US",
        count: int = 10,
        offset: int = 0,
        safe_search: SafeSearch | None = None,
    ) -> SearchResponse:
        """Search bing.com — the web SERP.

        Args:
            query: Search keywords, e.g. ``"coffee machine"``.
            market: Bing market code, e.g. ``"en-US"``, ``"de-DE"``.
            count: Number of results to return.
            offset: Zero-based result offset for pagination.
            safe_search: Adult-content filter — ``"off"``, ``"moderate"``
                or ``"strict"``.

        Returns:
            SearchResponse with organic results, ads and related searches.

        Raises:
            AuthenticationError: If the API key is invalid.
            ValidationError: If the parameters are invalid.

        Example:
            ```python
            results = await client.bing.search.search("laptop", market="de-DE")
            print(results.total_results, results.result_count)
            ```
        """
        params: dict[str, Any] = {
            "query": query,
            "market": market,
            "count": count,
            "offset": offset,
            "safe_search": safe_search,
        }
        response = await self._client.get("/v1/bing/search", params=params)
        return SearchResponse.model_validate(response)

    async def autocomplete(
        self,
        query: str,
        *,
        market: str = "en-US",
    ) -> AutocompleteResponse:
        """Bing search-box suggestions.

        Args:
            query: Partial search term, e.g. ``"coff"``.
            market: Bing market code, e.g. ``"en-US"``.

        Returns:
            AutocompleteResponse with Bing's suggestions for the term.

        Example:
            ```python
            result = await client.bing.search.autocomplete("coff")
            for s in result.suggestions:
                print(s)
            ```
        """
        params: dict[str, Any] = {"query": query, "market": market}
        response = await self._client.get("/v1/bing/autocomplete", params=params)
        return AutocompleteResponse.model_validate(response)
