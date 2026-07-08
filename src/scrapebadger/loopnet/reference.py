"""LoopNet Reference Data API client.

Provides the static coverage-market and property-type lists.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from scrapebadger.loopnet.models import MarketsResponse, PropertyTypesResponse

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class ReferenceClient:
    """Client for LoopNet reference endpoints (markets, property types).

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            markets = await client.loopnet.reference.markets()
            for m in markets.markets:
                print(f"{m.code}: {m.name} ({m.currency})")

            types = await client.loopnet.reference.property_types()
            for t in types.property_types:
                print(t.slug, t.name)
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize reference client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def markets(self) -> MarketsResponse:
        """List LoopNet coverage markets (us/ca/uk/fr/es). Free (0 credits).

        Returns:
            Markets response with all supported coverage markets.

        Example:
            ```python
            result = await client.loopnet.reference.markets()
            for m in result.markets:
                print(f"{m.code}: {m.name} ({m.domain})")
            ```
        """
        response = await self._client.get("/v1/loopnet/markets")
        return MarketsResponse.model_validate(response)

    async def property_types(self) -> PropertyTypesResponse:
        """List LoopNet property-type facets. Free (0 credits).

        Returns:
            Property-types response with all searchable property-type slugs.

        Example:
            ```python
            result = await client.loopnet.reference.property_types()
            for t in result.property_types:
                print(f"{t.slug}: {t.name}")
            ```
        """
        response = await self._client.get("/v1/loopnet/property-types")
        return PropertyTypesResponse.model_validate(response)
