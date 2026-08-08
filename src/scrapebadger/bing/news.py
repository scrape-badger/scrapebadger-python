"""Bing News API client.

The Bing news vertical.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from scrapebadger.bing.models import NewsResponse

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient

Freshness = Literal["day", "week", "month"]


class NewsClient:
    """Client for the Bing news endpoint.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            news = await client.bing.news.news("artificial intelligence")
            for article in news.results:
                print(article.source, article.published_at, article.title)
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize news client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def news(
        self,
        query: str,
        *,
        market: str = "en-US",
        freshness: Freshness | None = None,
    ) -> NewsResponse:
        """Search the Bing news vertical.

        Args:
            query: Search keywords, e.g. ``"artificial intelligence"``.
            market: Bing market code, e.g. ``"en-US"``.
            freshness: Restrict article age — ``"day"``, ``"week"`` or
                ``"month"``.

        Returns:
            NewsResponse with articles carrying publisher, publish dates and
            real URLs.

        Example:
            ```python
            news = await client.bing.news.news("ai", freshness="day")
            for article in news.results:
                print(article.title, article.published_utc)
            ```
        """
        params: dict[str, Any] = {
            "query": query,
            "market": market,
            "freshness": freshness,
        }
        response = await self._client.get("/v1/bing/news", params=params)
        return NewsResponse.model_validate(response)
