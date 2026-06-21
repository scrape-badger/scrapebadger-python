"""eBay Items API client.

Provides methods for fetching a single listing's full detail and its catalog
product reviews.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.ebay.models import ItemDetailResponse, ReviewsResponse

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class ItemsClient:
    """Client for eBay item endpoints (detail, reviews).

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            detail = await client.ebay.items.get_item("123456789012")
            print(detail.item.title)

            reviews = await client.ebay.items.get_item_reviews("123456789012")
            print(f"{reviews.ratings_total} ratings")
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize items client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def get_item(
        self,
        item_id: str,
        *,
        domain: str = "com",
    ) -> ItemDetailResponse:
        """Get a single eBay listing's full detail.

        Args:
            item_id: The eBay item id.
            domain: eBay marketplace domain (e.g. "com", "de"). Defaults to "com".

        Returns:
            Item detail response including images, shipping, seller, and item specifics.

        Raises:
            NotFoundError: If the item doesn't exist.
            AuthenticationError: If the API key is invalid.

        Example:
            ```python
            detail = await client.ebay.items.get_item("123456789012", domain="de")
            item = detail.item
            print(f"{item.title}: {item.price.raw if item.price else 'N/A'}")
            ```
        """
        params: dict[str, Any] = {"domain": domain}
        response = await self._client.get(f"/v1/ebay/items/{item_id}", params=params)
        return ItemDetailResponse.model_validate(response)

    async def get_item_reviews(
        self,
        item_id: str,
        *,
        product_id: str | None = None,
        domain: str = "com",
        page: int = 1,
    ) -> ReviewsResponse:
        """Get catalog product reviews shown on an eBay listing.

        Args:
            item_id: The eBay item id.
            product_id: Optional eBay catalog product id to scope the reviews.
            domain: eBay marketplace domain (e.g. "com", "de"). Defaults to "com".
            page: Page number (1-indexed). Defaults to 1.

        Returns:
            Reviews response with reviews, aggregate rating, and star histogram.

        Example:
            ```python
            reviews = await client.ebay.items.get_item_reviews("123456789012")
            for r in reviews.reviews:
                print(f"{r.rating}* {r.title}")
            ```
        """
        params: dict[str, Any] = {
            "domain": domain,
            "page": page,
            "product_id": product_id,
        }
        response = await self._client.get(f"/v1/ebay/items/{item_id}/reviews", params=params)
        return ReviewsResponse.model_validate(response)
