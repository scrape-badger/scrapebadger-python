"""Amazon Products API client.

Provides methods for fetching product detail, offers, and reviews by ASIN.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.amazon.models import (
    OffersResponse,
    ProductDetailResponse,
    ReviewsResponse,
)

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class ProductsClient:
    """Client for Amazon product endpoints (detail, offers, reviews).

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            detail = await client.amazon.products.get("B08N5WRWNW")
            print(detail.product.title)

            offers = await client.amazon.products.offers("B08N5WRWNW")
            print(f"{offers.total_offers} offers")

            reviews = await client.amazon.products.reviews("B08N5WRWNW")
            print(f"{reviews.ratings_total} ratings")
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize products client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def get(
        self,
        asin: str,
        *,
        domain: str = "com",
        zip: str | None = None,
        language: str | None = None,
    ) -> ProductDetailResponse:
        """Get full product detail (PDP) for an ASIN.

        Args:
            asin: The product ASIN.
            domain: Amazon marketplace domain (e.g. "com", "de"). Defaults to "com".
            zip: Delivery ZIP / postal code for localized price & availability.
            language: Preferred content language (e.g. "en_US").

        Returns:
            Product detail response including variants, badges, buybox, and related products.

        Raises:
            NotFoundError: If the product doesn't exist.
            AuthenticationError: If the API key is invalid.

        Example:
            ```python
            detail = await client.amazon.products.get("B08N5WRWNW", domain="de")
            product = detail.product
            print(f"{product.title}: {product.price.raw if product.price else 'N/A'}")
            ```
        """
        params: dict[str, Any] = {"domain": domain, "zip": zip, "language": language}
        response = await self._client.get(f"/v1/amazon/products/{asin}", params=params)
        return ProductDetailResponse.model_validate(response)

    async def offers(
        self,
        asin: str,
        *,
        domain: str = "com",
        zip: str | None = None,
    ) -> OffersResponse:
        """Get all-seller offers (and the buybox winner) for an ASIN.

        Args:
            asin: The product ASIN.
            domain: Amazon marketplace domain (e.g. "com", "de"). Defaults to "com".
            zip: Delivery ZIP / postal code for localized price & availability.

        Returns:
            Offers response with the buybox winner and full offer list.

        Example:
            ```python
            offers = await client.amazon.products.offers("B08N5WRWNW")
            for offer in offers.offers:
                print(f"{offer.seller.name if offer.seller else '?'}: "
                      f"{offer.price.raw if offer.price else '?'}")
            ```
        """
        params: dict[str, Any] = {"domain": domain, "zip": zip}
        response = await self._client.get(f"/v1/amazon/products/{asin}/offers", params=params)
        return OffersResponse.model_validate(response)

    async def reviews(
        self,
        asin: str,
        *,
        domain: str = "com",
        page: int = 1,
        sort_by: str | None = None,
        star: str | None = None,
        verified_only: bool | None = None,
        media_only: bool | None = None,
    ) -> ReviewsResponse:
        """Get product reviews for an ASIN.

        Args:
            asin: The product ASIN.
            domain: Amazon marketplace domain (e.g. "com", "de"). Defaults to "com".
            page: Page number (1-indexed). Defaults to 1.
            sort_by: Sort order ("helpful" or "recent").
            star: Filter by star rating (e.g. "five_star", "one_star").
            verified_only: Restrict to verified-purchase reviews.
            media_only: Restrict to reviews containing images / video.

        Returns:
            Reviews response with reviews, aggregate rating, and breakdown.

        Example:
            ```python
            reviews = await client.amazon.products.reviews(
                "B08N5WRWNW", sort_by="recent", verified_only=True,
            )
            for r in reviews.reviews:
                print(f"{r.rating}* {r.title}")
            ```
        """
        params: dict[str, Any] = {
            "domain": domain,
            "page": page,
            "sort_by": sort_by,
            "star": star,
            "verified_only": verified_only,
            "media_only": media_only,
        }
        response = await self._client.get(f"/v1/amazon/products/{asin}/reviews", params=params)
        return ReviewsResponse.model_validate(response)
