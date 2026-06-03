"""Amazon Sellers API client.

Provides methods for seller profile, storefront products, and buyer feedback.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.amazon.models import (
    SellerFeedbackResponse,
    SellerProductsResponse,
    SellerProfileResponse,
)

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class SellersClient:
    """Client for Amazon seller endpoints (profile, products, feedback).

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            profile = await client.amazon.sellers.get("A2L77EE7U53NWQ")
            print(profile.seller.name)

            products = await client.amazon.sellers.products("A2L77EE7U53NWQ")
            for p in products.products:
                print(p.title)
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize sellers client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def get(
        self,
        seller_id: str,
        *,
        domain: str = "com",
    ) -> SellerProfileResponse:
        """Get a seller's profile and ratings.

        Args:
            seller_id: The seller ID.
            domain: Amazon marketplace domain (e.g. "com", "de"). Defaults to "com".

        Returns:
            Seller profile response.

        Raises:
            NotFoundError: If the seller doesn't exist.
            AuthenticationError: If the API key is invalid.

        Example:
            ```python
            profile = await client.amazon.sellers.get("A2L77EE7U53NWQ")
            print(f"{profile.seller.name}: {profile.seller.rating}*")
            ```
        """
        params: dict[str, Any] = {"domain": domain}
        response = await self._client.get(f"/v1/amazon/sellers/{seller_id}", params=params)
        return SellerProfileResponse.model_validate(response)

    async def products(
        self,
        seller_id: str,
        *,
        domain: str = "com",
        page: int = 1,
    ) -> SellerProductsResponse:
        """Get a seller's storefront listings.

        Args:
            seller_id: The seller ID.
            domain: Amazon marketplace domain (e.g. "com", "de"). Defaults to "com".
            page: Page number (1-indexed). Defaults to 1.

        Returns:
            Seller products response with result rows and pagination.

        Example:
            ```python
            result = await client.amazon.sellers.products("A2L77EE7U53NWQ", page=2)
            for p in result.products:
                print(p.title)
            ```
        """
        params: dict[str, Any] = {"domain": domain, "page": page}
        response = await self._client.get(f"/v1/amazon/sellers/{seller_id}/products", params=params)
        return SellerProductsResponse.model_validate(response)

    async def feedback(
        self,
        seller_id: str,
        *,
        domain: str = "com",
        page: int = 1,
    ) -> SellerFeedbackResponse:
        """Get buyer feedback entries for a seller.

        Args:
            seller_id: The seller ID.
            domain: Amazon marketplace domain (e.g. "com", "de"). Defaults to "com".
            page: Page number (1-indexed). Defaults to 1.

        Returns:
            Seller feedback response with feedback entries and pagination.

        Example:
            ```python
            result = await client.amazon.sellers.feedback("A2L77EE7U53NWQ")
            for f in result.feedback:
                print(f"{f.rating}*: {f.comment}")
            ```
        """
        params: dict[str, Any] = {"domain": domain, "page": page}
        response = await self._client.get(f"/v1/amazon/sellers/{seller_id}/feedback", params=params)
        return SellerFeedbackResponse.model_validate(response)
