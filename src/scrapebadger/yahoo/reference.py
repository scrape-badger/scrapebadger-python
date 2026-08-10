"""Yahoo Reference Data API client.

The supported-market list.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from scrapebadger.yahoo.models import MarketsResponse

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class ReferenceClient:
    """Client for Yahoo reference data endpoints (markets).

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            markets = await client.yahoo.reference.markets()
            for m in markets.markets:
                print(f"{m.code}: {m.name} ({m.country}) — {m.host}")
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize reference client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def markets(self) -> MarketsResponse:
        """Get all supported Yahoo markets.

        Yahoo Japan (``search.yahoo.co.jp``) is a separate engine and is not
        covered by this API.

        Returns:
            MarketsResponse with every Yahoo market code, name, country and
            regional search host.

        Example:
            ```python
            result = await client.yahoo.reference.markets()
            for m in result.markets:
                print(f"{m.code}: {m.name}")
            ```
        """
        response = await self._client.get("/v1/yahoo/markets")
        return MarketsResponse.model_validate(response)
