"""Realtor Reference Data API client.

Provides the method for fetching the static list of supported markets.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from scrapebadger.realtor.models import MarketsResponse

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class ReferenceClient:
    """Client for Realtor reference data endpoints (markets).

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            markets = await client.realtor.reference.list_markets()
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
        """Get all supported Realtor markets.

        Returns:
            Markets response with all supported markets (us, ca).

        Example:
            ```python
            result = await client.realtor.reference.list_markets()
            for m in result.markets:
                print(f"{m.code}: {m.name} ({m.domain})")
            ```
        """
        response = await self._client.get("/v1/realtor/markets")
        return MarketsResponse.model_validate(response)
