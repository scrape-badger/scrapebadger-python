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
        category: int = 0,
        gprop: str = "",
    ) -> dict[str, Any]:
        """Interest over time for one or more search terms.

        Args:
            q: Up to 5 comma-separated terms.
            geo: Geographic location code (empty = worldwide).
            date: Time range like ``now 1-H``, ``today 12-m``, ``all``, or
                custom ``YYYY-MM-DD YYYY-MM-DD``.
            category: Category filter id (``0`` = all).
            gprop: Property filter — ``""``, ``images``, ``news``,
                ``froogle``, or ``youtube``.
        """
        params: dict[str, Any] = {
            "q": q,
            "geo": geo,
            "date": date,
            "category": category,
            "gprop": gprop,
        }
        return await self._client.get("/v1/google/trends/interest", params=params)

    async def regions(
        self,
        q: str,
        *,
        geo: str = "",
        date: str = "today 12-m",
        resolution: str = "auto",
    ) -> dict[str, Any]:
        """Interest broken down by region for a search term.

        Args:
            q: Search term.
            geo: Geographic location (empty = worldwide).
            date: Time range — same shape as :meth:`interest`.
            resolution: Region granularity — ``auto`` (default), ``COUNTRY``,
                ``REGION``, ``DMA`` or ``CITY``. Google has a hierarchy:
                you can't ask for country-level data inside a specific
                country, so ``auto`` lets the widget pick.
        """
        params: dict[str, Any] = {
            "q": q,
            "geo": geo,
            "date": date,
            "resolution": resolution,
        }
        return await self._client.get("/v1/google/trends/regions", params=params)

    async def related(
        self,
        q: str,
        *,
        geo: str = "",
        date: str = "today 12-m",
    ) -> dict[str, Any]:
        """Related topics and queries for a search term.

        Returns both ``related_topics`` (Knowledge Graph entities with
        ``rising``/``top`` buckets) and ``related_queries`` (string queries
        with ``rising``/``top`` buckets) in a single response.
        """
        params: dict[str, Any] = {"q": q, "geo": geo, "date": date}
        return await self._client.get("/v1/google/trends/related", params=params)

    async def trending(
        self,
        *,
        geo: str = "US",
        hl: str = "en-US",
        hours: int = 24,
    ) -> dict[str, Any]:
        """Real-time trending searches via the TrendsUi batchexecute backend.

        Args:
            geo: Country code (ISO 3166 alpha-2).
            hl: Language code (e.g. ``en-US``).
            hours: Look-back window — Google supports ``24`` (default),
                ``48``, ``168`` (= 1 week).
        """
        params: dict[str, Any] = {"geo": geo, "hl": hl, "hours": hours}
        return await self._client.get("/v1/google/trends/trending", params=params)

    async def trending_now(
        self,
        *,
        geo: str = "US",
        hours: int = 24,
        category: str = "all",
        status: str = "all",
        sort: str = "relevance",
        hl: str = "en-US",
    ) -> dict[str, Any]:
        """Current trending searches with the full Google Trends UI filter set.

        Args:
            geo: Country code (e.g. ``US``, ``LT``, ``GB``).
            hours: Look-back window — ``4``, ``24`` (default), ``48``, ``168``.
            category: Category filter — ``all`` (default), ``business``,
                ``entertainment``, ``health``, ``sci_tech``, ``sports``,
                ``top_stories``. Letter codes (``b``/``e``/``m``/``t``/
                ``s``/``h``) also accepted.
            status: Trend state — ``all`` (default) or ``active`` (only
                trends with non-zero search volume).
            sort: Sort order — ``relevance`` (default), ``search_volume``,
                ``title``, or ``recency``.
            hl: Language code.
        """
        params: dict[str, Any] = {
            "geo": geo,
            "hours": hours,
            "category": category,
            "status": status,
            "sort": sort,
            "hl": hl,
        }
        return await self._client.get("/v1/google/trends/trending-now", params=params)

    async def search(
        self,
        q: str,
        *,
        data_type: str = "TIMESERIES",
        geo: str = "",
        date: str = "today 12-m",
        cat: int = 0,
        gprop: str = "",
        region: str | None = None,
        language: str | None = None,
        tz: str = "0",
    ) -> dict[str, Any]:
        """Unified Google Trends query — pick the response shape via ``data_type``.

        ``data_type``: ``TIMESERIES`` (default) | ``GEO_MAP`` |
        ``GEO_MAP_0`` | ``RELATED_TOPICS`` | ``RELATED_QUERIES``.
        """
        params: dict[str, Any] = {
            "q": q,
            "data_type": data_type,
            "geo": geo,
            "date": date,
            "cat": cat,
            "gprop": gprop,
            "tz": tz,
        }
        if region is not None:
            params["region"] = region
        if language is not None:
            params["language"] = language
        return await self._client.get("/v1/google/trends/search", params=params)

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
