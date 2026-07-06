"""Zillow Reference Data API client.

Provides the method for fetching the static list of coverage markets.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from scrapebadger.zillow.models import MarketsResponse

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class ReferenceClient:
    """Client for Zillow reference data endpoints (markets).

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            markets = await client.zillow.reference.list_markets()
            for m in markets.markets:
                print(f"{m.code}: {m.domain} ({m.currency})")
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize reference client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def list_markets(self) -> MarketsResponse:
        """Get all supported Zillow coverage markets.

        Returns:
            Markets response with all coverage regions (US + Canada, all served
            via zillow.com).

        Example:
            ```python
            result = await client.zillow.reference.list_markets()
            for m in result.markets:
                print(f"{m.code}: {m.name} ({m.domain})")
            ```
        """
        response = await self._client.get("/v1/zillow/markets")
        return MarketsResponse.model_validate(response)
