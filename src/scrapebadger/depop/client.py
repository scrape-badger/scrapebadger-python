"""Depop API client.

Depop endpoints: search (product grid), get_product (full single-listing
detail, by slug), get_user (shop/seller profile), get_user_products (a
seller's product grid), and list_markets. All methods are async and return
strongly-typed Pydantic models. Single global host (depop.com) localised by
``market`` — the market code selects country and currency (us, gb [alias uk],
au, ie, it, fr, de, es, nl, nz).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.depop.models import (
    MarketsResponse,
    ProductDetail,
    SearchResponse,
    ShopProfile,
    UserProductsResponse,
)

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class DepopClient:
    """Client for all Depop API operations.

    Depop is a second-hand fashion marketplace. There is one global host
    (depop.com) localised by ``market`` (us, gb [alias uk], au, ie, it, fr, de,
    es, nl, nz), which selects the country and currency the storefront renders
    in. Search and user-products return card grids (24 per page, ``page``-based
    pagination); get_product and get_user return full detail.

    Example:
        ```python
        from scrapebadger import ScrapeBadger

        async with ScrapeBadger(api_key="your-key") as client:
            # Search products
            results = await client.depop.search("nike vintage")
            for card in results.products:
                print(f"{card.slug} — {card.price}")

            # Full product detail
            detail = await client.depop.get_product("some-product-slug")
            print(detail.title)

            # Shop profile + their products
            shop = await client.depop.get_user("someseller")
            listings = await client.depop.get_user_products("someseller")

            # Supported markets
            markets = await client.depop.list_markets()
        ```

    Note:
        Depop data is browser-rendered (cloakbrowser), so calls take a few
        seconds to complete.

        This client is not instantiated directly. Instead, access it through
        the `depop` property of the main `ScrapeBadger` client.
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize Depop client.

        Args:
            client: The base HTTP client for making API requests.
        """
        self._client = client

    async def search(
        self,
        query: str,
        *,
        market: str = "us",
        per_page: int = 24,
        page: int = 1,
        price_min: float | None = None,
        price_max: float | None = None,
        brands: str | None = None,
        sizes: str | None = None,
        colours: str | None = None,
        conditions: str | None = None,
        gender: str | None = None,
        sort: str | None = None,
    ) -> SearchResponse:
        """Search Depop for products.

        Args:
            query: Search term (required).
            market: Market code (us, gb [alias uk], au, ie, it, fr, de, es, nl,
                nz). Defaults to "us".
            per_page: Cards per page. Defaults to 24.
            page: Page number (``page``-based pagination). Defaults to 1.
            price_min: Minimum price filter.
            price_max: Maximum price filter.
            brands: Comma-separated brand filter.
            sizes: Comma-separated size filter.
            colours: Comma-separated colour filter.
            conditions: Comma-separated condition filter.
            gender: Gender filter.
            sort: Sort order.

        Returns:
            Search response with matching product cards and pagination.

        Raises:
            AuthenticationError: If the API key is invalid.
            ValidationError: If the parameters are invalid.

        Example:
            ```python
            results = await client.depop.search(
                "nike vintage",
                market="gb",
                price_max=100,
                sort="priceAscending",
            )
            print(f"Page {results.meta.page}")
            ```
        """
        params: dict[str, Any] = {
            "query": query,
            "market": market,
            "per_page": per_page,
            "page": page,
            "price_min": price_min,
            "price_max": price_max,
            "brands": brands,
            "sizes": sizes,
            "colours": colours,
            "conditions": conditions,
            "gender": gender,
            "sort": sort,
        }
        response = await self._client.get("/v1/depop/search", params=params)
        return SearchResponse.model_validate(response)

    async def get_product(self, slug: str, *, market: str = "us") -> ProductDetail:
        """Get a single Depop product's full detail by slug.

        Args:
            slug: The Depop product slug.
            market: Market code (us, gb [alias uk], au, ie, it, fr, de, es, nl,
                nz). Defaults to "us".

        Returns:
            Product detail response.

        Raises:
            NotFoundError: If the product doesn't exist.
            AuthenticationError: If the API key is invalid.

        Example:
            ```python
            detail = await client.depop.get_product("some-product-slug")
            print(detail.title, detail.price)
            ```
        """
        params: dict[str, Any] = {"market": market}
        response = await self._client.get(f"/v1/depop/products/{slug}", params=params)
        return ProductDetail.model_validate(response)

    async def get_user(self, username: str, *, market: str = "us") -> ShopProfile:
        """Get a Depop seller's shop profile.

        Args:
            username: The Depop seller username.
            market: Market code (us, gb [alias uk], au, ie, it, fr, de, es, nl,
                nz). Defaults to "us".

        Returns:
            Shop profile response.

        Raises:
            NotFoundError: If the user doesn't exist.
            AuthenticationError: If the API key is invalid.

        Example:
            ```python
            shop = await client.depop.get_user("someseller")
            print(shop.name, shop.follower_count)
            ```
        """
        params: dict[str, Any] = {"market": market}
        response = await self._client.get(f"/v1/depop/users/{username}", params=params)
        return ShopProfile.model_validate(response)

    async def get_user_products(
        self,
        username: str,
        *,
        market: str = "us",
        per_page: int = 24,
        page: int = 1,
    ) -> UserProductsResponse:
        """Get a Depop seller's product grid.

        Args:
            username: The Depop seller username.
            market: Market code (us, gb [alias uk], au, ie, it, fr, de, es, nl,
                nz). Defaults to "us".
            per_page: Cards per page. Defaults to 24.
            page: Page number (``page``-based pagination). Defaults to 1.

        Returns:
            User products response with the seller's product cards and
            pagination.

        Raises:
            NotFoundError: If the user doesn't exist.
            AuthenticationError: If the API key is invalid.

        Example:
            ```python
            listings = await client.depop.get_user_products("someseller")
            for card in listings.products:
                print(card.slug, card.price)
            ```
        """
        params: dict[str, Any] = {
            "market": market,
            "per_page": per_page,
            "page": page,
        }
        response = await self._client.get(f"/v1/depop/users/{username}/products", params=params)
        return UserProductsResponse.model_validate(response)

    async def list_markets(self) -> MarketsResponse:
        """Get all supported Depop coverage markets.

        Returns:
            Markets response with all supported markets.

        Example:
            ```python
            result = await client.depop.list_markets()
            for m in result.markets:
                print(f"{m.code}: {m.name} ({m.currency})")
            ```
        """
        response = await self._client.get("/v1/depop/markets")
        return MarketsResponse.model_validate(response)

    # --- BEGIN generated by sdk/codegen/facade — do not edit ---

    async def get_product_detail(self, product_id: str, *, market: str = "us") -> dict[str, Any]:
        """Get product detail.

        Generated from the OpenAPI spec; returns the raw response dict.
        """
        params = {k: v for k, v in {"market": market}.items() if v is not None}
        return await self._client.get(f"/v1/depop/products/{product_id}", params=params)

    # --- END generated by sdk/codegen/facade ---
