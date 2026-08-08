"""DuckDuckGo Web Search API client."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.duckduckgo.models import SearchResponse

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class SearchClient:
    """Client for the DuckDuckGo web search endpoint.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            results = await client.duckduckgo.search.search("python asyncio")
            for r in results.results:
                print(r.title, r.url)
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
        region: str = "wt-wt",
        safesearch: str = "moderate",
        timelimit: str = "",
        page: int = 1,
    ) -> SearchResponse:
        """Search DuckDuckGo web results.

        Args:
            query: Search keywords, e.g. ``"python asyncio"``.
            region: Region code, e.g. ``"us-en"``. Default ``"wt-wt"`` (no region).
            safesearch: ``"on"``, ``"moderate"``, or ``"off"``.
            timelimit: Recency filter — ``"d"``, ``"w"``, ``"m"``, ``"y"``, or ``""``.
            page: Page number.

        Returns:
            SearchResponse with the organic results and the optional abstract box.

        Raises:
            AuthenticationError: If the API key is invalid.
            ValidationError: If the parameters are invalid.

        Example:
            ```python
            results = await client.duckduckgo.search.search(
                "climate news", region="us-en", timelimit="w"
            )
            print(results.result_count, results.has_next)
            ```
        """
        params: dict[str, Any] = {
            "query": query,
            "region": region,
            "safesearch": safesearch,
            "timelimit": timelimit,
            "page": page,
        }
        response = await self._client.get("/v1/duckduckgo/search", params=params)
        return SearchResponse.model_validate(response)
