"""eBay Sellers API client.

Provides methods for seller profile, storefront listings, and feedback.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.ebay.models import (
    SellerFeedbackResponse,
    SellerItemsResponse,
    SellerProfileResponse,
)

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class SellersClient:
    """Client for eBay seller endpoints (profile, items, feedback).

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            profile = await client.ebay.sellers.get_seller("musicmagpie")
            print(profile.seller.feedback_score)

            items = await client.ebay.sellers.get_seller_items("musicmagpie")
            for it in items.results:
                print(it.title)
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize sellers client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def get_seller(
        self,
        username: str,
        *,
        domain: str = "com",
    ) -> SellerProfileResponse:
        """Get an eBay seller's public profile.

        Args:
            username: The seller's username.
            domain: eBay marketplace domain (e.g. "com", "de"). Defaults to "com".

        Returns:
            Seller profile response.

        Raises:
            NotFoundError: If the seller doesn't exist.
            AuthenticationError: If the API key is invalid.

        Example:
            ```python
            profile = await client.ebay.sellers.get_seller("musicmagpie")
            print(f"{profile.seller.username}: {profile.seller.feedback_percent}%")
            ```
        """
        params: dict[str, Any] = {"domain": domain}
        response = await self._client.get(f"/v1/ebay/sellers/{username}", params=params)
        return SellerProfileResponse.model_validate(response)

    async def get_seller_items(
        self,
        username: str,
        *,
        domain: str = "com",
        query: str | None = None,
        page: int = 1,
        per_page: int | None = None,
    ) -> SellerItemsResponse:
        """List the active listings of a single eBay seller.

        Args:
            username: The seller's username.
            domain: eBay marketplace domain (e.g. "com", "de"). Defaults to "com".
            query: Optional keyword filter within the seller's listings.
            page: Page number (1-indexed). Defaults to 1.
            per_page: Results per page (60, 120 or 240; clamped).

        Returns:
            Seller items response with result cards and pagination.

        Example:
            ```python
            result = await client.ebay.sellers.get_seller_items("musicmagpie", page=2)
            for it in result.results:
                print(it.title)
            ```
        """
        params: dict[str, Any] = {
            "domain": domain,
            "query": query,
            "page": page,
            "per_page": per_page,
        }
        response = await self._client.get(f"/v1/ebay/sellers/{username}/items", params=params)
        return SellerItemsResponse.model_validate(response)

    async def get_seller_feedback(
        self,
        username: str,
        *,
        domain: str = "com",
        page: int = 1,
    ) -> SellerFeedbackResponse:
        """Get a seller's recent feedback comments.

        Args:
            username: The seller's username.
            domain: eBay marketplace domain (e.g. "com", "de"). Defaults to "com".
            page: Page number (1-indexed). Defaults to 1.

        Returns:
            Seller feedback response with feedback entries and pagination.

        Example:
            ```python
            result = await client.ebay.sellers.get_seller_feedback("musicmagpie")
            for f in result.feedback:
                print(f"{f.rating}: {f.comment}")
            ```
        """
        params: dict[str, Any] = {"domain": domain, "page": page}
        response = await self._client.get(f"/v1/ebay/sellers/{username}/feedback", params=params)
        return SellerFeedbackResponse.model_validate(response)
