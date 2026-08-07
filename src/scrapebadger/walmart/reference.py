"""Walmart Reference Data API client.

The supported-market list and the service health check.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.walmart.models import MarketsResponse

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class ReferenceClient:
    """Client for Walmart reference data endpoints (markets, health).

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            markets = await client.walmart.reference.list_markets()
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
        """Get all supported Walmart markets.

        Returns:
            MarketsResponse. Only walmart.com (``US``) is supported —
            walmart.ca and walmart.com.mx run on different platforms with
            different payload shapes, so they are not claimed here.

        Example:
            ```python
            result = await client.walmart.reference.list_markets()
            for m in result.markets:
                print(f"{m.code}: {m.name} ({m.domain})")
            ```
        """
        response = await self._client.get("/v1/walmart/markets")
        return MarketsResponse.model_validate(response)

    async def health(self) -> dict[str, Any]:
        """Check the Walmart scraper service health.

        Returns:
            The raw health payload from the Walmart scraper service.

        Example:
            ```python
            status = await client.walmart.reference.health()
            print(status["status"])
            ```
        """
        return await self._client.get("/v1/walmart/health")
