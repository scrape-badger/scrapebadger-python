"""TikTok Reference Data API client.

Provides methods for fetching the supported content-region list and a
service health check.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.tiktok.models import RegionsResponse

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class ReferenceClient:
    """Client for TikTok reference data endpoints (regions).

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            regions = await client.tiktok.reference.regions()
            for r in regions.regions:
                print(f"{r.code}: {r.name} ({r.locale})")
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize reference client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def regions(self) -> RegionsResponse:
        """List supported TikTok content regions.

        Returns:
            Regions response with all supported content regions.

        Example:
            ```python
            result = await client.tiktok.reference.regions()
            for r in result.regions:
                print(f"{r.code}: {r.name}")
            ```
        """
        response = await self._client.get("/v1/tiktok/regions")
        return RegionsResponse.model_validate(response)

    async def health(self) -> dict[str, Any]:
        """Check the TikTok scraper service health.

        Returns:
            The raw health payload from the TikTok scraper service.

        Example:
            ```python
            status = await client.tiktok.reference.health()
            print(status)
            ```
        """
        response = await self._client.get("/v1/tiktok/health")
        return dict(response)
