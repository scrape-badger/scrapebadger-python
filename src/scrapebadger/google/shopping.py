"""Google Shopping client (search, product detail, click enrichment)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class ShoppingClient:
    """Client for Google Shopping endpoints.

    Exposes:
    - `search`: product listings with prices, ratings, thumbnails, filters
    - `product`: detailed product + seller list
    - `click`: per-product merchant URL enrichment (materializes the direct
       merchant link that Google strips from organic Shopping HTML)

    Example:
        ```python
        products = await client.google.shopping.search("laptop", max_price=1000)
        first = products["results"][0]
        # Resolve the direct merchant URL for this product
        enriched = await client.google.shopping.click(
            title=first["title"],
            source=first["source"],
        )
        print("Merchant URL:", enriched["merchant_url"])
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        self._client = client

    async def search(
        self,
        q: str,
        *,
        gl: str = "us",
        min_price: int | None = None,
        max_price: int | None = None,
        sort_by: str | None = None,
    ) -> dict[str, Any]:
        """Search Google Shopping for products.

        Args:
            q: Product search query.
            gl: Country code.
            min_price: Minimum price filter.
            max_price: Maximum price filter.
            sort_by: One of "price_low", "price_high", "rating", "reviews".

        Returns:
            A response with:
            - `results`: product list (title, price, source, rating, thumbnail,
              product_id, click_link, ...)
            - `filters`: quick filters (on sale, free shipping, etc.)
            - `ads`: sponsored PLA listings
            - `pagination`
        """
        params: dict[str, Any] = {"q": q, "gl": gl}
        if min_price is not None:
            params["min_price"] = min_price
        if max_price is not None:
            params["max_price"] = max_price
        if sort_by:
            params["sort_by"] = sort_by
        return await self._client.get("/v1/google/shopping/search", params=params)

    async def product(
        self,
        product_id: str,
        *,
        gl: str = "us",
    ) -> dict[str, Any]:
        """Get detailed product information by product ID."""
        params: dict[str, Any] = {"product_id": product_id, "gl": gl}
        return await self._client.get("/v1/google/shopping/product", params=params)

    async def click(
        self,
        title: str,
        *,
        source: str | None = None,
        q: str | None = None,
        product_id: str | None = None,
        gl: str = "us",
        hl: str = "en",
    ) -> dict[str, Any]:
        """Resolve the real merchant URL for a Shopping product.

        Google has removed merchant links from organic Shopping HTML, so
        this per-product enrichment uses an "I'm Feeling Lucky" redirect
        (scoped to the card's `source` merchant when known) to return the
        direct product page URL. Mirrors ScrapingDog's
        `scrapingdog_immersive_product_link` pattern.

        Args:
            title: Exact product title from a search result.
            source: Merchant source name from the shopping card (e.g.
                "Walmart", "Best Buy"). When supplied, the lookup is scoped
                to that merchant via `site:` operator for more accurate
                matching.
            q: Original search query (optional, improves disambiguation).
            product_id: Stable product_id from the search result — echoed
                back in the response.
            gl: Country code.
            hl: Language code.

        Returns:
            Dict with `product_id`, `title`, `merchant_url`, `merchant_domain`,
            `source_query`.

        Example:
            ```python
            result = await client.google.shopping.click(
                title='Razer Blade 14" 3K OLED Gaming Laptop',
                source="Razer.com",
            )
            print(result["merchant_url"])
            # https://www.razer.com/gaming-laptops/razer-blade-14
            ```
        """
        params: dict[str, Any] = {"title": title, "gl": gl, "hl": hl}
        if source:
            params["source"] = source
        if q:
            params["q"] = q
        if product_id:
            params["product_id"] = product_id
        return await self._client.get(
            "/v1/google/shopping/product/click",
            params=params,
        )
