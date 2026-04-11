"""Google News client."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class NewsClient:
    """Client for Google News endpoints (search, topics, trending).

    Example:
        ```python
        articles = await client.google.news.search("openai", max_results=20)
        for a in articles["articles"]:
            print(a["title"], a["source"]["name"])
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        self._client = client

    async def search(
        self,
        q: str,
        *,
        hl: str = "en",
        gl: str = "US",
        max_results: int = 10,
    ) -> dict[str, Any]:
        """Search Google News articles."""
        params: dict[str, Any] = {
            "q": q,
            "hl": hl,
            "gl": gl,
            "max_results": max_results,
        }
        return await self._client.get("/v1/google/news/search", params=params)

    async def topics(
        self,
        topic: str,
        *,
        hl: str = "en",
        gl: str = "US",
        max_results: int = 10,
    ) -> dict[str, Any]:
        """Get news for a predefined topic.

        Args:
            topic: One of "WORLD", "BUSINESS", "TECHNOLOGY", "ENTERTAINMENT",
                "SPORTS", "SCIENCE", "HEALTH".
        """
        params: dict[str, Any] = {
            "topic": topic,
            "hl": hl,
            "gl": gl,
            "max_results": max_results,
        }
        return await self._client.get("/v1/google/news/topics", params=params)

    async def trending(
        self,
        *,
        hl: str = "en",
        gl: str = "US",
        max_results: int = 10,
    ) -> dict[str, Any]:
        """Get trending news stories."""
        params: dict[str, Any] = {
            "hl": hl,
            "gl": gl,
            "max_results": max_results,
        }
        return await self._client.get("/v1/google/news/trending", params=params)
