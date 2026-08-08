"""Yandex Reference API client.

The list of supported Yandex markets.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from scrapebadger.yandex.models import MarketsResponse

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class ReferenceClient:
    """Client for the Yandex markets endpoint.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            markets = await client.yandex.reference.markets()
            for m in markets.markets:
                print(m.code, m.domain, m.default_lr)
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize reference client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def markets(self) -> MarketsResponse:
        """Get all supported Yandex markets.

        Returns:
            MarketsResponse with the market codes, domains, and default regions.

        Example:
            ```python
            result = await client.yandex.reference.markets()
            for m in result.markets:
                print(f"{m.code}: {m.name} ({m.domain})")
            ```
        """
        response = await self._client.get("/v1/yandex/markets")
        return MarketsResponse.model_validate(response)
