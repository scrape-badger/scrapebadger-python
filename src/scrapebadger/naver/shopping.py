"""Naver Shopping API client.

Provides methods for shopping rankings, insight, categories, finder search,
deals, verticals, brand ranking, catalog search, and price comparison, plus
the Shopping Live sub-client via the ``live`` property.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.naver.live import LiveClient
from scrapebadger.naver.models import (
    PriceCompareResponse,
    ShoppingBestsellersResponse,
    ShoppingBrandCategoriesResponse,
    ShoppingBrandRankResponse,
    ShoppingCatalogSearchResponse,
    ShoppingCategoriesResponse,
    ShoppingCategoryTreeResponse,
    ShoppingDealsResponse,
    ShoppingFilteredProductsResponse,
    ShoppingInsightResponse,
    ShoppingItItemsResponse,
    ShoppingKeywordPeriodsResponse,
    ShoppingKeywordRankResponse,
    ShoppingSearchFiltersResponse,
    ShoppingSearchProductsResponse,
    ShoppingVerticalResponse,
)

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class ShoppingClient:
    """Client for Naver Shopping endpoints.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            top = await client.naver.shopping.bestsellers()
            cards = await client.naver.shopping.search_products("노트북")
            offers = await client.naver.shopping.price_compare("아이폰 15")
            live = await client.naver.shopping.live.broadcast("1234567")
        ```

    Attributes:
        live: Sub-client for Shopping Live (broadcasts, channels, shortclips).
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize shopping client.

        Args:
            client: The base HTTP client.
        """
        self._client = client
        self._live = LiveClient(client)

    @property
    def live(self) -> LiveClient:
        """Access Shopping Live endpoints.

        Returns:
            LiveClient for broadcasts, channels, and shortclips.
        """
        return self._live

    async def bestsellers(
        self,
        *,
        category_id: str = "ALL",
        age_type: str = "ALL",
        sort_type: str = "PRODUCT_CLICK",
        period_type: str = "DAILY",
    ) -> ShoppingBestsellersResponse:
        """Get the shopping bestseller ranking.

        Args:
            category_id: Category id or "ALL". Defaults to "ALL".
            age_type: Shopper age bucket or "ALL". Defaults to "ALL".
            sort_type: "PRODUCT_CLICK" or "PRODUCT_BUY". Defaults to "PRODUCT_CLICK".
            period_type: "DAILY" or "WEEKLY". Defaults to "DAILY".

        Returns:
            Shopping bestsellers response.
        """
        params: dict[str, Any] = {
            "category_id": category_id,
            "age_type": age_type,
            "sort_type": sort_type,
            "period_type": period_type,
        }
        response = await self._client.get("/v1/naver/shopping/bestsellers", params=params)
        return ShoppingBestsellersResponse.model_validate(response)

    async def keywords(
        self,
        category_id: str,
        *,
        age_type: str = "ALL",
        sort_type: str = "KEYWORD_POPULAR",
        period_type: str = "WEEKLY",
    ) -> ShoppingKeywordRankResponse:
        """Get the shopping keyword ranking for a category.

        Args:
            category_id: Naver Shopping category id.
            age_type: Shopper age bucket or "ALL". Defaults to "ALL".
            sort_type: Keyword sort type. Defaults to "KEYWORD_POPULAR".
            period_type: "DAILY" or "WEEKLY". Defaults to "WEEKLY".

        Returns:
            Shopping keyword ranking response.
        """
        params: dict[str, Any] = {
            "category_id": category_id,
            "age_type": age_type,
            "sort_type": sort_type,
            "period_type": period_type,
        }
        response = await self._client.get("/v1/naver/shopping/keywords", params=params)
        return ShoppingKeywordRankResponse.model_validate(response)

    async def insight(
        self,
        category_id: str,
        start_date: str,
        end_date: str,
        *,
        time_unit: str = "date",
        age: str = "",
        gender: str = "",
        device: str = "",
        count: int = 20,
    ) -> ShoppingInsightResponse:
        """Get shopping insight top keywords for a category and date range.

        Args:
            category_id: Naver Shopping category id.
            start_date: Range start, YYYY-MM-DD.
            end_date: Range end, YYYY-MM-DD.
            time_unit: "date", "week", or "month". Defaults to "date".
            age: Age filter. Defaults to "".
            gender: Gender filter ("", "f", or "m"). Defaults to "".
            device: Device filter ("", "pc", or "mo"). Defaults to "".
            count: Top keywords to return (1..100). Defaults to 20.

        Returns:
            Shopping insight response.
        """
        params: dict[str, Any] = {
            "category_id": category_id,
            "start_date": start_date,
            "end_date": end_date,
            "time_unit": time_unit,
            "age": age,
            "gender": gender,
            "device": device,
            "count": count,
        }
        response = await self._client.get("/v1/naver/shopping/insight", params=params)
        return ShoppingInsightResponse.model_validate(response)

    async def categories(self) -> ShoppingCategoriesResponse:
        """Get the top-level shopping categories.

        Returns:
            Shopping categories response.
        """
        response = await self._client.get("/v1/naver/shopping/categories")
        return ShoppingCategoriesResponse.model_validate(response)

    async def search_products(
        self,
        query: str,
        *,
        tab: str = "m_view",
    ) -> ShoppingSearchProductsResponse:
        """Search finder shopping product cards (preview).

        Args:
            query: Search query.
            tab: Finder tab ("m_view" or "m_shop"). Defaults to "m_view".

        Returns:
            Shopping search products response.
        """
        params: dict[str, Any] = {"query": query, "tab": tab}
        response = await self._client.get("/v1/naver/shopping/search-products", params=params)
        return ShoppingSearchProductsResponse.model_validate(response)

    async def search_filters(self, query: str) -> ShoppingSearchFiltersResponse:
        """Get the available filters (brands/attributes) for a search query.

        Args:
            query: Search query.

        Returns:
            Shopping search filters response.
        """
        params: dict[str, Any] = {"query": query}
        response = await self._client.get("/v1/naver/shopping/search-filters", params=params)
        return ShoppingSearchFiltersResponse.model_validate(response)

    async def deals(self, gender: str) -> ShoppingDealsResponse:
        """Get snxbest gendered deal products.

        Args:
            gender: "M" or "F".

        Returns:
            Shopping deals response.
        """
        params: dict[str, Any] = {"gender": gender}
        response = await self._client.get("/v1/naver/shopping/deals", params=params)
        return ShoppingDealsResponse.model_validate(response)

    async def vertical(self, vertical: str) -> ShoppingVerticalResponse:
        """Get snxbest vertical products.

        Args:
            vertical: "fashiontown", "shoppinglive", or "logistics".

        Returns:
            Shopping vertical response.
        """
        response = await self._client.get(f"/v1/naver/shopping/verticals/{vertical}")
        return ShoppingVerticalResponse.model_validate(response)

    async def it_items(self) -> ShoppingItItemsResponse:
        """Get the snxbest "IT items" curated cards.

        Returns:
            Shopping IT items response.
        """
        response = await self._client.get("/v1/naver/shopping/it-items")
        return ShoppingItItemsResponse.model_validate(response)

    async def category_tree(
        self,
        *,
        parent_id: str | None = None,
    ) -> ShoppingCategoryTreeResponse:
        """Get the shopping category tree (one level).

        Args:
            parent_id: Parent category id; omit for the top level.

        Returns:
            Shopping category tree response.
        """
        params: dict[str, Any] = {"parent_id": parent_id}
        response = await self._client.get("/v1/naver/shopping/category-tree", params=params)
        return ShoppingCategoryTreeResponse.model_validate(response)

    async def search_filtered(
        self,
        query: str,
        *,
        brand_id: str | None = None,
        attribute_id: str | None = None,
    ) -> ShoppingFilteredProductsResponse:
        """Search filtered finder shopping products (brand/attribute).

        Args:
            query: Search query.
            brand_id: Finder filterSet brand value id.
            attribute_id: FilterSet attribute value id.

        Returns:
            Shopping filtered products response.
        """
        params: dict[str, Any] = {
            "query": query,
            "brand_id": brand_id,
            "attribute_id": attribute_id,
        }
        response = await self._client.get("/v1/naver/shopping/search-filtered", params=params)
        return ShoppingFilteredProductsResponse.model_validate(response)

    async def brand_rank(
        self,
        *,
        category_id: str = "A",
        age_type: str = "ALL",
        sort_type: str = "BRAND_POPULAR",
        period_type: str = "WEEKLY",
    ) -> ShoppingBrandRankResponse:
        """Get the snxbest brand ranking (top 20 fixed list).

        Args:
            category_id: Category id or "A". Defaults to "A".
            age_type: Shopper age bucket or "ALL". Defaults to "ALL".
            sort_type: "BRAND_POPULAR" or "BRAND_ISSUE". Defaults to "BRAND_POPULAR".
            period_type: "WEEKLY" or "MONTHLY". Defaults to "WEEKLY".

        Returns:
            Shopping brand rank response.
        """
        params: dict[str, Any] = {
            "category_id": category_id,
            "age_type": age_type,
            "sort_type": sort_type,
            "period_type": period_type,
        }
        response = await self._client.get("/v1/naver/shopping/brand-rank", params=params)
        return ShoppingBrandRankResponse.model_validate(response)

    async def brand_categories(
        self,
        *,
        parent_id: str | None = None,
    ) -> ShoppingBrandCategoriesResponse:
        """Get the snxbest brand-ranking category tree (DIV1, or DIV2 children).

        Args:
            parent_id: Parent category id; omit for the top level (DIV1).

        Returns:
            Shopping brand categories response.
        """
        params: dict[str, Any] = {"parent_id": parent_id}
        response = await self._client.get("/v1/naver/shopping/brand-categories", params=params)
        return ShoppingBrandCategoriesResponse.model_validate(response)

    async def keyword_periods(
        self,
        *,
        category_id: str = "A",
        age_type: str = "ALL",
        sort_type: str = "KEYWORD_NEW",
        period_type: str = "WEEKLY",
    ) -> ShoppingKeywordPeriodsResponse:
        """Get the available snxbest keyword-rank periods.

        Args:
            category_id: Category id or "A". Defaults to "A".
            age_type: Shopper age bucket or "ALL". Defaults to "ALL".
            sort_type: Keyword sort type. Defaults to "KEYWORD_NEW".
            period_type: "WEEKLY" or "MONTHLY". Defaults to "WEEKLY".

        Returns:
            Shopping keyword periods response.
        """
        params: dict[str, Any] = {
            "category_id": category_id,
            "age_type": age_type,
            "sort_type": sort_type,
            "period_type": period_type,
        }
        response = await self._client.get("/v1/naver/shopping/keyword-periods", params=params)
        return ShoppingKeywordPeriodsResponse.model_validate(response)

    async def search_catalog(
        self,
        query: str,
        *,
        sort: str = "RECOMMEND",
        page: int = 1,
    ) -> ShoppingCatalogSearchResponse:
        """Full-catalog shopping search (SSR page 1 + paged XHR pages 2-5).

        Args:
            query: Search query (1..200 chars).
            sort: "RECOMMEND", "LOW_PRICE", "HIGH_PRICE", "PURCHASE", "REVIEW",
                or "RECENT". Defaults to "RECOMMEND".
            page: Result page (1..5). Defaults to 1.

        Returns:
            Shopping catalog search response.
        """
        params: dict[str, Any] = {"query": query, "sort": sort, "page": page}
        response = await self._client.get("/v1/naver/shopping/search-catalog", params=params)
        return ShoppingCatalogSearchResponse.model_validate(response)

    async def price_compare(self, query: str) -> PriceCompareResponse:
        """Get seller offers per catalog product (가격비교).

        Args:
            query: Search query (1..200 chars).

        Returns:
            Price compare response.
        """
        params: dict[str, Any] = {"query": query}
        response = await self._client.get("/v1/naver/shopping/price-compare", params=params)
        return PriceCompareResponse.model_validate(response)
