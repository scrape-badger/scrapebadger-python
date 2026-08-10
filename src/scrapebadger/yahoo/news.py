"""Yahoo News API client.

The Yahoo news vertical.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.yahoo.models import NewsResponse

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class NewsClient:
    """Client for the Yahoo news endpoint.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            news = await client.yahoo.news.news("artificial intelligence")
            for article in news.results:
                print(article.source, article.published, article.title)
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
        market: str = "us",
    ) -> NewsResponse:
        """Search the Yahoo news vertical.

        Args:
            query: Search keywords, e.g. ``"artificial intelligence"``.
            market: Yahoo market code, e.g. ``"us"``.

        Returns:
            NewsResponse with articles carrying publisher, syndication
            source and real URLs. ``published`` is a relative age string
            (``"26 minutes ago"``) — Yahoo renders no absolute date.

        Example:
            ```python
            news = await client.yahoo.news.news("ai")
            for article in news.results:
                print(article.title, article.published)
            ```
        """
        params: dict[str, Any] = {"query": query, "market": market}
        response = await self._client.get("/v1/yahoo/news", params=params)
        return NewsResponse.model_validate(response)
