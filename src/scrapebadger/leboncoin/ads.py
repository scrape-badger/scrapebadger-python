"""Leboncoin Ads API client.

Provides methods for fetching a single ad's full detail and its similar ads.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.leboncoin.models import AdResponse, SimilarResponse

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class AdsClient:
    """Client for Leboncoin ad endpoints (detail, similar).

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            detail = await client.leboncoin.ads.get_ad(2812345678)
            print(detail.ad.subject)

            similar = await client.leboncoin.ads.get_similar(2812345678)
            print(f"{len(similar.ads)} similar ads")
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize ads client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def get_ad(self, list_id: int) -> AdResponse:
        """Get a single Leboncoin ad's full detail.

        Args:
            list_id: The Leboncoin ad id.

        Returns:
            Ad detail response including images, attributes, location, and owner.

        Raises:
            NotFoundError: If the ad doesn't exist.
            AuthenticationError: If the API key is invalid.

        Example:
            ```python
            detail = await client.leboncoin.ads.get_ad(2812345678)
            ad = detail.ad
            print(f"{ad.subject}: {ad.price_eur} {ad.currency}")
            ```
        """
        response = await self._client.get(f"/v1/leboncoin/ads/{list_id}")
        return AdResponse.model_validate(response)

    async def get_similar(self, list_id: int, *, limit: int | None = None) -> SimilarResponse:
        """Get ads similar to a given Leboncoin ad.

        Args:
            list_id: The Leboncoin ad id.
            limit: Maximum number of similar ads to return.

        Returns:
            Similar response with the source list id and matching ads.

        Example:
            ```python
            result = await client.leboncoin.ads.get_similar(2812345678, limit=10)
            for ad in result.ads:
                print(ad.subject)
            ```
        """
        params: dict[str, Any] = {"limit": limit}
        response = await self._client.get(f"/v1/leboncoin/ads/{list_id}/similar", params=params)
        return SimilarResponse.model_validate(response)
