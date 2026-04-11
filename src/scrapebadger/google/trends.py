"""Google Trends client."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class TrendsClient:
    """Client for Google Trends endpoints.

    Example:
        ```python
        interest = await client.google.trends.interest(
            "python,javascript",
            date="today 12-m",
            geo="US",
        )
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        self._client = client

    async def interest(
        self,
        q: str,
        *,
        geo: str = "",
        date: str = "today 12-m",
    ) -> dict[str, Any]:
        """Interest over time for one or more search terms.

        Args:
            q: Up to 5 comma-separated terms.
            geo: Geographic location code (empty = worldwide).
            date: Time range like "now 1-H", "today 12-m", "all", or
                custom "YYYY-MM-DD YYYY-MM-DD".
        """
        params: dict[str, Any] = {"q": q, "geo": geo, "date": date}
        return await self._client.get("/v1/google/trends/interest", params=params)

    async def regions(
        self,
        q: str,
        *,
        geo: str = "",
    ) -> dict[str, Any]:
        """Interest broken down by region."""
        params: dict[str, Any] = {"q": q, "geo": geo}
        return await self._client.get("/v1/google/trends/regions", params=params)

    async def related(
        self,
        q: str,
        *,
        geo: str = "",
    ) -> dict[str, Any]:
        """Related topics and queries for a search term."""
        params: dict[str, Any] = {"q": q, "geo": geo}
        return await self._client.get("/v1/google/trends/related", params=params)

    async def trending(
        self,
        *,
        geo: str = "US",
    ) -> dict[str, Any]:
        """Real-time trending searches for a region."""
        params: dict[str, Any] = {"geo": geo}
        return await self._client.get("/v1/google/trends/trending", params=params)

    async def autocomplete(
        self,
        q: str,
        *,
        hl: str = "en-US",
        tz: str = "0",
    ) -> dict[str, Any]:
        """Return categorized Knowledge Graph topic entities for a query prefix.

        Unlike Google Search autocomplete (flat keyword suggestions), this
        returns topic entities each tagged with a Knowledge Graph `mid`, a
        semantic `type` ("Topic", "Sports", "Career", etc.), and a direct
        link into Google Trends explore.

        Args:
            q: Query prefix to resolve into Trends topics.
            hl: Language code (default "en-US").
            tz: Timezone offset in minutes.
        """
        params: dict[str, Any] = {"q": q, "hl": hl, "tz": tz}
        return await self._client.get("/v1/google/trends/autocomplete", params=params)
