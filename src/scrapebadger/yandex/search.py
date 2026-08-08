"""Yandex Web Search API client."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.yandex.models import SearchResponse

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class SearchClient:
    """Client for the Yandex web search endpoint.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            results = await client.yandex.search.search("python asyncio")
            for r in results.organic_results:
                print(r.position, r.title, r.url)
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
        domain: str = "tr",
        page: int = 1,
        lr: int | None = None,
        lang: str | None = None,
    ) -> SearchResponse:
        """Search Yandex web results.

        Args:
            query: Search keywords, e.g. ``"python asyncio"``.
            domain: Market domain — ``"tr"`` (default), ``"com"``, ``"ru"``,
                ``"by"``, ``"kz"``, ``"uz"``.
            page: Page number (1-25).
            lr: Yandex region id (``lr``), e.g. ``213`` for Moscow.
            lang: UI/results language code, e.g. ``"en"``.

        Returns:
            SearchResponse with organic results, ads, inline media, related
            searches, and the pagination block.

        Raises:
            AuthenticationError: If the API key is invalid.
            ValidationError: If the parameters are invalid.

        Example:
            ```python
            results = await client.yandex.search.search(
                "погода", domain="ru", lr=213
            )
            print(results.result_count)
            ```
        """
        params: dict[str, Any] = {
            "query": query,
            "domain": domain,
            "page": page,
            "lr": lr,
            "lang": lang,
        }
        response = await self._client.get("/v1/yandex/search", params=params)
        return SearchResponse.model_validate(response)
