"""Yahoo Search API client.

Web search and search-box autocomplete.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from scrapebadger.yahoo.models import AutocompleteResponse, SearchResponse

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient

SafeSearch = Literal["off", "moderate", "strict"]


class SearchClient:
    """Client for Yahoo web search and autocomplete endpoints.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            results = await client.yahoo.search.search("coffee machine")
            for r in results.results:
                print(f"{r.position}. {r.title} — {r.url}")

            suggestions = await client.yahoo.search.autocomplete("coff")
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
        market: str = "us",
        offset: int = 0,
        safe_search: SafeSearch | None = None,
    ) -> SearchResponse:
        """Search yahoo.com — the web SERP.

        Yahoo serves 7 organic results per page, so ``offset`` moves in steps
        of 7 (page 2 is ``offset=7``). There is no page-size parameter.

        Args:
            query: Search keywords, e.g. ``"coffee machine"``.
            market: Yahoo market code, e.g. ``"us"``, ``"de"``. Lowercase.
            offset: Zero-based absolute result offset for pagination.
            safe_search: Adult-content filter — ``"off"``, ``"moderate"``
                or ``"strict"``.

        Returns:
            SearchResponse with organic results, ads and related searches.

        Raises:
            AuthenticationError: If the API key is invalid.
            ValidationError: If the parameters are invalid.

        Example:
            ```python
            results = await client.yahoo.search.search("laptop", market="de")
            print(results.result_count)
            ```
        """
        params: dict[str, Any] = {
            "query": query,
            "market": market,
            "offset": offset,
            "safe_search": safe_search,
        }
        response = await self._client.get("/v1/yahoo/search", params=params)
        return SearchResponse.model_validate(response)

    async def autocomplete(
        self,
        query: str,
        *,
        market: str = "us",
    ) -> AutocompleteResponse:
        """Yahoo search-box suggestions.

        Args:
            query: Partial search term, e.g. ``"coff"``.
            market: Yahoo market code, e.g. ``"us"``.

        Returns:
            AutocompleteResponse with Yahoo's suggestions for the term.

        Example:
            ```python
            result = await client.yahoo.search.autocomplete("coff")
            for s in result.suggestions:
                print(s)
            ```
        """
        params: dict[str, Any] = {"query": query, "market": market}
        response = await self._client.get("/v1/yahoo/autocomplete", params=params)
        return AutocompleteResponse.model_validate(response)
