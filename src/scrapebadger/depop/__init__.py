"""Depop API module for ScrapeBadger SDK.

This module provides an async client for scraping Depop second-hand fashion
marketplace data through the ScrapeBadger API. All methods are async and return
strongly-typed Pydantic models.

Example:
    ```python
    from scrapebadger import ScrapeBadger

    async with ScrapeBadger(api_key="your-key") as client:
        # Search products
        results = await client.depop.search("nike vintage")
        for card in results.products:
            print(f"{card.slug} — {card.price}")

        # Get product detail
        detail = await client.depop.get_product("some-product-slug")
        print(detail.title)

        # Get a shop profile
        shop = await client.depop.get_user("someseller")
        print(shop.name)
    ```
"""

from scrapebadger.depop.client import DepopClient
from scrapebadger.depop.models import (
    DepopCard,
    Market,
    MarketsResponse,
    ProductDetail,
    SearchMeta,
    SearchResponse,
    ShopProfile,
    UserProductsResponse,
)

__all__ = [
    # Cards
    "DepopCard",
    # Client
    "DepopClient",
    # Markets
    "Market",
    "MarketsResponse",
    # Product detail
    "ProductDetail",
    # Search / user-products
    "SearchMeta",
    "SearchResponse",
    # Shop profile
    "ShopProfile",
    "UserProductsResponse",
]
