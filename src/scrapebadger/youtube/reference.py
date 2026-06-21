"""YouTube Reference Data API client.

Provides methods for the static category, language, region, and market lists.
These endpoints are free (0 credits).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.youtube.models import (
    CategoriesResponse,
    LanguagesResponse,
    MarketsResponse,
    RegionsResponse,
)

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class ReferenceClient:
    """Client for YouTube reference data endpoints (categories, languages, regions, markets).

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            categories = await client.youtube.reference.list_categories(gl="US")
            for c in categories.categories:
                print(f"{c.id}: {c.title}")

            markets = await client.youtube.reference.list_markets()
            for m in markets.markets:
                print(f"{m.gl}/{m.hl}: {m.name}")
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize reference client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def list_categories(self, *, gl: str = "US") -> CategoriesResponse:
        """List YouTube video categories (Data-API parity).

        Args:
            gl: Content region whose category set to return. Defaults to "US".

        Returns:
            Categories response with category id/title rows.

        Example:
            ```python
            result = await client.youtube.reference.list_categories(gl="GB")
            for c in result.categories:
                print(f"{c.id}: {c.title}")
            ```
        """
        params: dict[str, Any] = {"gl": gl}
        response = await self._client.get("/v1/youtube/categories", params=params)
        return CategoriesResponse.model_validate(response)

    async def list_languages(self) -> LanguagesResponse:
        """List supported UI languages (hl codes).

        Returns:
            Languages response with language id/title rows.

        Example:
            ```python
            result = await client.youtube.reference.list_languages()
            for lang in result.languages:
                print(f"{lang.id}: {lang.title}")
            ```
        """
        response = await self._client.get("/v1/youtube/languages")
        return LanguagesResponse.model_validate(response)

    async def list_regions(self) -> RegionsResponse:
        """List supported content regions (gl codes).

        Returns:
            Regions response with region id/title rows.

        Example:
            ```python
            result = await client.youtube.reference.list_regions()
            for region in result.regions:
                print(f"{region.id}: {region.title}")
            ```
        """
        response = await self._client.get("/v1/youtube/regions")
        return RegionsResponse.model_validate(response)

    async def list_markets(self) -> MarketsResponse:
        """List the regions the scraper explicitly geo-targets (proxy-pinned).

        Returns:
            Markets response with the supported scraper markets.

        Example:
            ```python
            result = await client.youtube.reference.list_markets()
            for m in result.markets:
                print(f"{m.gl}/{m.hl}: {m.name}")
            ```
        """
        response = await self._client.get("/v1/youtube/markets")
        return MarketsResponse.model_validate(response)
