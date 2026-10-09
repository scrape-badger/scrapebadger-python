"""Naver Products API client.

Provides methods for product detail, review summary, review list, Q&A list,
variant group graph, and group-level review summary.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.naver.models import (
    GroupProductGraphResponse,
    GroupReviewSummaryResponse,
    PaginatedReviewsResponse,
    ProductDetailResponse,
    ProductQnaResponse,
    ProductReviewSummaryResponse,
)

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class ProductsClient:
    """Client for Naver commerce product endpoints.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            detail = await client.naver.products.get("1234567890")
            summary = await client.naver.products.review_summary("1234567890")
            reviews = await client.naver.products.reviews(
                "1234567890", store_url="somestore", product_no="9876543210",
            )
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
        product_no: str,
        *,
        host: str = "brand",
        store_url: str | None = None,
        channel_uid: str | None = None,
        broadcast_id: str | None = None,
        live_channel_id: str | None = None,
        query: str | None = None,
    ) -> ProductDetailResponse:
        """Get full product detail (PDP).

        Args:
            product_no: Channel product no.
            host: "brand" or "smartstore". Defaults to "brand".
            store_url: Store slug; required when channel_uid is omitted.
            channel_uid: Opaque storefront channel key; overrides store-home resolution.
            broadcast_id: SmartStore partial-enrich only.
            live_channel_id: SmartStore partial-enrich only.
            query: SmartStore partial-enrich only (m.search query matched to the card).

        Returns:
            Product detail response.
        """
        params: dict[str, Any] = {
            "host": host,
            "store_url": store_url,
            "channel_uid": channel_uid,
            "broadcast_id": broadcast_id,
            "live_channel_id": live_channel_id,
            "query": query,
        }
        response = await self._client.get(f"/v1/naver/products/{product_no}", params=params)
        return ProductDetailResponse.model_validate(response)

    async def review_summary(
        self,
        origin_product_no: str,
        *,
        leaf_category_id: str | None = None,
    ) -> ProductReviewSummaryResponse:
        """Get a product rating summary.

        Args:
            origin_product_no: Origin product no.
            leaf_category_id: Leaf category id.

        Returns:
            Product review summary response.
        """
        params: dict[str, Any] = {"leaf_category_id": leaf_category_id}
        response = await self._client.get(
            f"/v1/naver/products/{origin_product_no}/review-summary", params=params
        )
        return ProductReviewSummaryResponse.model_validate(response)

    async def reviews(
        self,
        origin_product_no: str,
        *,
        store_url: str,
        product_no: str,
        host: str = "smartstore",
        channel_uid: str | None = None,
        checkout_merchant_no: int | None = None,
        page: int = 1,
        sort: str = "REVIEW_RANKING",
    ) -> PaginatedReviewsResponse:
        """Get a paginated product review list.

        Args:
            origin_product_no: Origin product no.
            store_url: Store URL slug (required).
            product_no: Channel product no (required).
            host: "brand" or "smartstore". Defaults to "smartstore".
            channel_uid: Storefront channel key.
            checkout_merchant_no: Checkout merchant no.
            page: Result page, 1-based. Defaults to 1.
            sort: Sort order. Defaults to "REVIEW_RANKING".

        Returns:
            Paginated reviews response.
        """
        params: dict[str, Any] = {
            "store_url": store_url,
            "product_no": product_no,
            "host": host,
            "channel_uid": channel_uid,
            "checkout_merchant_no": checkout_merchant_no,
            "page": page,
            "sort": sort,
        }
        response = await self._client.get(
            f"/v1/naver/products/{origin_product_no}/reviews", params=params
        )
        return PaginatedReviewsResponse.model_validate(response)

    async def qnas(
        self,
        origin_product_no: str,
        *,
        store_url: str,
        product_no: str,
        host: str = "smartstore",
        channel_uid: str | None = None,
        page: int = 1,
    ) -> ProductQnaResponse:
        """Get a paginated product Q&A list.

        Args:
            origin_product_no: Origin product no.
            store_url: Store URL slug (required).
            product_no: Channel product no (required).
            host: "brand" or "smartstore". Defaults to "smartstore".
            channel_uid: Storefront channel key (required when host=smartstore).
            page: Result page, 1-based. Defaults to 1.

        Returns:
            Product Q&A response.
        """
        params: dict[str, Any] = {
            "store_url": store_url,
            "product_no": product_no,
            "host": host,
            "channel_uid": channel_uid,
            "page": page,
        }
        response = await self._client.get(
            f"/v1/naver/products/{origin_product_no}/qnas", params=params
        )
        return ProductQnaResponse.model_validate(response)

    async def group(self, origin_product_no: str) -> GroupProductGraphResponse:
        """Get the storefront variant-group graph for a product.

        Args:
            origin_product_no: Origin product no.

        Returns:
            Group product graph response.
        """
        response = await self._client.get(f"/v1/naver/products/{origin_product_no}/group")
        return GroupProductGraphResponse.model_validate(response)

    async def group_review_summary(
        self,
        group_product_no: str,
        *,
        leaf_category_id: str,
    ) -> GroupReviewSummaryResponse:
        """Get a group-level rating summary.

        Args:
            group_product_no: Group product no.
            leaf_category_id: Leaf category id (required).

        Returns:
            Group review summary response.
        """
        params: dict[str, Any] = {"leaf_category_id": leaf_category_id}
        response = await self._client.get(
            f"/v1/naver/product-groups/{group_product_no}/review-summary", params=params
        )
        return GroupReviewSummaryResponse.model_validate(response)
