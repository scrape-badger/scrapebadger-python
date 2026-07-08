"""LoopNet Listings API client.

Provides full listing detail lookup by listing id.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.loopnet.models import ListingResponse

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class ListingsClient:
    """Client for the LoopNet listing detail endpoint.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            detail = await client.loopnet.listings.get("12345678")
            print(detail.listing.address, detail.listing.price_text)
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize listings client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def get(self, listing_id: str, *, market: str = "us") -> ListingResponse:
        """Get a single LoopNet listing's full detail. Costs 12 credits.

        Args:
            listing_id: The LoopNet listing id.
            market: Coverage market ("us", "ca", "uk", "fr", "es"). Defaults to "us".

        Returns:
            Listing detail response.

        Raises:
            NotFoundError: If the listing doesn't exist.
            AuthenticationError: If the API key is invalid.

        Example:
            ```python
            detail = await client.loopnet.listings.get("12345678")
            for space in detail.listing.spaces:
                print(space.name, space.rent_text)
            ```
        """
        params: dict[str, Any] = {"market": market}
        response = await self._client.get(f"/v1/loopnet/listings/{listing_id}", params=params)
        return ListingResponse.model_validate(response)
