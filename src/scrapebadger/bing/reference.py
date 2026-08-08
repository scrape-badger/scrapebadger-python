"""Bing Reference Data API client.

The supported-market list.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from scrapebadger.bing.models import MarketsResponse

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class ReferenceClient:
    """Client for Bing reference data endpoints (markets).

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            markets = await client.bing.reference.markets()
            for m in markets.markets:
                print(f"{m.code}: {m.name} ({m.country})")
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize reference client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def markets(self) -> MarketsResponse:
        """Get all supported Bing markets.

        Returns:
            MarketsResponse with every Bing market code, name and country.

        Example:
            ```python
            result = await client.bing.reference.markets()
            for m in result.markets:
                print(f"{m.code}: {m.name}")
            ```
        """
        response = await self._client.get("/v1/bing/markets")
        return MarketsResponse.model_validate(response)
