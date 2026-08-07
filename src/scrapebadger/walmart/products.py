"""Walmart Products API client.

Full product detail (PDP) and paginated customer reviews.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.walmart.models import Product, ReviewsResponse

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class ProductsClient:
    """Client for Walmart product endpoints (detail, reviews).

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            product = await client.walmart.products.get_product("5689919121")
            print(product.name, product.price, product.upc)

            reviews = await client.walmart.products.get_reviews("5689919121")
            print(reviews.distribution.average_rating)
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize products client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def get_product(self, item_id: str) -> Product:
        """Get a Walmart product's full detail.

        Args:
            item_id: Walmart ``usItemId``, e.g. ``"5689919121"``. The SEO slug in
                a ``/ip/...`` URL is decorative — only the numeric id is needed.

        Returns:
            Product with pricing, fulfilment SLAs, specifications, variants,
            seller, return policy, and a sample of top reviews.

        Raises:
            NotFoundError: If the product doesn't exist.
            AuthenticationError: If the API key is invalid.

        Example:
            ```python
            product = await client.walmart.products.get_product("5689919121")
            for f in product.fulfillment_summary:
                print(f.fulfillment, f.delivery_date)
            ```
        """
        response = await self._client.get(f"/v1/walmart/products/{item_id}")
        return Product.model_validate(response)

    async def get_reviews(
        self,
        item_id: str,
        *,
        page: int = 1,
        sort: str | None = None,
    ) -> ReviewsResponse:
        """Get paginated customer reviews with the full star histogram.

        Args:
            item_id: Walmart ``usItemId``, e.g. ``"5689919121"``.
            page: Page number, 1-100. 10 reviews per page — Walmart's page size,
                not adjustable.
            sort: Review ordering — ``"relevancy"``, ``"submission-desc"``,
                ``"submission-asc"``, ``"rating-desc"``, ``"rating-asc"``,
                ``"helpful"``.

        Returns:
            ReviewsResponse with the reviews, the rating breakdown, the review
            aspects, and the most-helpful positive and negative reviews.

        Example:
            ```python
            reviews = await client.walmart.products.get_reviews(
                "5689919121", sort="rating-desc"
            )
            for r in reviews.reviews:
                print(f"{r.rating}* {r.title}")
            ```
        """
        params: dict[str, Any] = {"page": page, "sort": sort}
        response = await self._client.get(f"/v1/walmart/products/{item_id}/reviews", params=params)
        return ReviewsResponse.model_validate(response)
