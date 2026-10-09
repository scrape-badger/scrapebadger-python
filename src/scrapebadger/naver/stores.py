"""Naver Stores API client.

Provides methods for SmartStore / Brand store profile, categories, product
listings, and bestsellers by store URL slug.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.naver.models import (
    StoreBestsellersResponse,
    StoreCategoriesResponse,
    StoreProductsResponse,
    StoreProfileResponse,
)

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class StoresClient:
    """Client for Naver Stores endpoints (profile, categories, products).

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            store = await client.naver.stores.get("somestore")
            cats = await client.naver.stores.categories("somestore")
            products = await client.naver.stores.products("somestore")
            top = await client.naver.stores.bestsellers("somestore")
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize stores client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def get(
        self,
        store_url: str,
        *,
        host: str = "smartstore",
    ) -> StoreProfileResponse:
        """Get a store profile.

        Args:
            store_url: Store URL slug.
            host: "smartstore" or "brand". Defaults to "smartstore".

        Returns:
            Store profile response.
        """
        params: dict[str, Any] = {"host": host}
        response = await self._client.get(f"/v1/naver/stores/{store_url}", params=params)
        return StoreProfileResponse.model_validate(response)

    async def categories(
        self,
        store_url: str,
        *,
        host: str = "smartstore",
    ) -> StoreCategoriesResponse:
        """Get a store's category list.

        Args:
            store_url: Store URL slug.
            host: "smartstore" or "brand". Defaults to "smartstore".

        Returns:
            Store categories response.
        """
        params: dict[str, Any] = {"host": host}
        response = await self._client.get(f"/v1/naver/stores/{store_url}/categories", params=params)
        return StoreCategoriesResponse.model_validate(response)

    async def products(
        self,
        store_url: str,
        *,
        host: str = "smartstore",
        category_id: str | None = None,
        page: int = 1,
        size: int = 20,
        sort: str = "POPULARITY",
        channel_uid: str | None = None,
    ) -> StoreProductsResponse:
        """Get a store's product listing (listing card union, not full detail).

        Args:
            store_url: Store URL slug.
            host: "smartstore" or "brand". Defaults to "smartstore".
            category_id: Restrict to a store category.
            page: Result page, 1-based. Defaults to 1.
            size: Products per page. Defaults to 20.
            sort: Sort order. Defaults to "POPULARITY".
            channel_uid: With host=smartstore, routes through the brand-host lane.

        Returns:
            Store products response.
        """
        params: dict[str, Any] = {
            "host": host,
            "category_id": category_id,
            "page": page,
            "size": size,
            "sort": sort,
            "channel_uid": channel_uid,
        }
        response = await self._client.get(f"/v1/naver/stores/{store_url}/products", params=params)
        return StoreProductsResponse.model_validate(response)

    async def bestsellers(
        self,
        store_url: str,
        *,
        host: str = "smartstore",
        period: str = "DAILY",
    ) -> StoreBestsellersResponse:
        """Get a store's bestseller list.

        Args:
            store_url: Store URL slug.
            host: "smartstore" or "brand". Defaults to "smartstore".
            period: "REALTIME", "DAILY", "WEEKLY", or "MONTHLY". Defaults to "DAILY".

        Returns:
            Store bestsellers response.
        """
        params: dict[str, Any] = {"host": host, "period": period}
        response = await self._client.get(
            f"/v1/naver/stores/{store_url}/bestsellers", params=params
        )
        return StoreBestsellersResponse.model_validate(response)
