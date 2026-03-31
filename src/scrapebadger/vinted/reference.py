"""Vinted Reference Data API client.

Provides methods for fetching reference data such as brands, colors,
statuses, and available markets.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from scrapebadger.vinted.models import (
    BrandsResponse,
    ColorsResponse,
    MarketsResponse,
    StatusesResponse,
)

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class ReferenceClient:
    """Client for Vinted reference data endpoints.

    Provides async methods for fetching brands, colors, item condition
    statuses, and available markets. These are useful for building
    search filters.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            # Get available markets
            markets = await client.vinted.reference.markets()
            for m in markets.markets:
                print(f"{m.code}: {m.name} ({m.currency})")

            # Search brands
            brands = await client.vinted.reference.brands("nike", market="fr")
            for b in brands.brands:
                print(f"{b.title} (id={b.id})")

            # Get colors for a market
            colors = await client.vinted.reference.colors(market="de")
            for c in colors.colors:
                print(f"{c.title}: {c.hex}")
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize reference client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def brands(
        self,
        keyword: str | None = None,
        *,
        market: str = "fr",
        per_page: int = 20,
    ) -> BrandsResponse:
        """Search for Vinted brands.

        Args:
            keyword: Optional search keyword to filter brands.
            market: Vinted market code (e.g. "fr", "de"). Defaults to "fr".
            per_page: Number of brands per page. Defaults to 20.

        Returns:
            Brands response with matching brands.

        Example:
            ```python
            result = await client.vinted.reference.brands("adidas")
            for brand in result.brands:
                print(f"{brand.title} ({brand.item_count} items)")
            ```
        """
        response = await self._client.get(
            "/v1/vinted/brands",
            params={
                "keyword": keyword,
                "market": market,
                "per_page": per_page,
            },
        )
        return BrandsResponse.model_validate(response)

    async def colors(
        self,
        *,
        market: str = "fr",
    ) -> ColorsResponse:
        """Get available colors for a Vinted market.

        Args:
            market: Vinted market code (e.g. "fr", "de"). Defaults to "fr".

        Returns:
            Colors response with all available colors.

        Example:
            ```python
            result = await client.vinted.reference.colors(market="fr")
            for color in result.colors:
                print(f"{color.title} (#{color.hex})")
            ```
        """
        response = await self._client.get(
            "/v1/vinted/colors",
            params={"market": market},
        )
        return ColorsResponse.model_validate(response)

    async def statuses(
        self,
        *,
        market: str = "fr",
    ) -> StatusesResponse:
        """Get available item condition statuses for a Vinted market.

        Args:
            market: Vinted market code (e.g. "fr", "de"). Defaults to "fr".

        Returns:
            Statuses response with all available condition statuses.

        Example:
            ```python
            result = await client.vinted.reference.statuses(market="fr")
            for status in result.statuses:
                print(f"{status.id}: {status.title}")
            ```
        """
        response = await self._client.get(
            "/v1/vinted/statuses",
            params={"market": market},
        )
        return StatusesResponse.model_validate(response)

    async def markets(self) -> MarketsResponse:
        """Get all available Vinted markets.

        Returns:
            Markets response with all supported Vinted markets.

        Example:
            ```python
            result = await client.vinted.reference.markets()
            for market in result.markets:
                print(f"{market.code}: {market.name} ({market.domain})")
            ```
        """
        response = await self._client.get("/v1/vinted/markets")
        return MarketsResponse.model_validate(response)
