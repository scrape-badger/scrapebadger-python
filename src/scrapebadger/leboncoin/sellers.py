"""Leboncoin Sellers API client.

Provides methods for seller profile and seller listings.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.leboncoin.models import SellerListingsResponse, SellerResponse

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class SellersClient:
    """Client for Leboncoin seller endpoints (profile, listings).

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            profile = await client.leboncoin.sellers.get_seller("12345678")
            print(profile.seller.name)

            listings = await client.leboncoin.sellers.get_seller_listings("12345678")
            for ad in listings.ads:
                print(ad.subject)
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize sellers client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def get_seller(self, user_id: str) -> SellerResponse:
        """Get a Leboncoin seller's public profile.

        Args:
            user_id: The seller's user id.

        Returns:
            Seller profile response.

        Raises:
            NotFoundError: If the seller doesn't exist.
            AuthenticationError: If the API key is invalid.

        Example:
            ```python
            profile = await client.leboncoin.sellers.get_seller("12345678")
            print(f"{profile.seller.name}: {profile.seller.total_ads} ads")
            ```
        """
        response = await self._client.get(f"/v1/leboncoin/sellers/{user_id}")
        return SellerResponse.model_validate(response)

    async def get_seller_listings(
        self,
        user_id: str,
        *,
        page: int = 1,
        limit: int | None = None,
    ) -> SellerListingsResponse:
        """List the active ads of a single Leboncoin seller.

        Args:
            user_id: The seller's user id.
            page: Page number (1-indexed). Defaults to 1.
            limit: Results per page.

        Returns:
            Seller listings response with ads and pagination.

        Example:
            ```python
            result = await client.leboncoin.sellers.get_seller_listings("12345678", page=2)
            for ad in result.ads:
                print(ad.subject)
            ```
        """
        params: dict[str, Any] = {"page": page, "limit": limit}
        response = await self._client.get(
            f"/v1/leboncoin/sellers/{user_id}/listings", params=params
        )
        return SellerListingsResponse.model_validate(response)
