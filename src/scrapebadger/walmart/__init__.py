"""Walmart API module for ScrapeBadger SDK.

This module provides a comprehensive async client for scraping walmart.com
through the ScrapeBadger API. All methods are async and return strongly-typed
Pydantic models. Walmart is US-only — walmart.com is the single supported
market, so no method takes a market/country parameter.

Example:
    ```python
    from scrapebadger import ScrapeBadger

    async with ScrapeBadger(api_key="your-key") as client:
        # Search
        results = await client.walmart.search.search("laptop")
        for item in results.items:
            print(f"{item.position}. {item.name} — ${item.price}")

        # Product detail
        product = await client.walmart.products.get_product("5689919121")
        print(product.name, product.upc, product.rating)

        # Seller profile
        seller = await client.walmart.sellers.get_seller("101040442")
        print(seller.seller.name, seller.seller.rating)
    ```
"""

from scrapebadger.walmart.client import WalmartClient
from scrapebadger.walmart.models import (
    AutocompleteResponse,
    Badge,
    Breadcrumb,
    ConditionOffer,
    EmbeddedSeller,
    FulfillmentOption,
    FulfillmentSummary,
    Image,
    LocationContext,
    Market,
    MarketsResponse,
    NameValue,
    NutritionFacts,
    Price,
    PriceInfo,
    PriceRange,
    Product,
    Promotion,
    RatingDistribution,
    ReturnPolicy,
    Review,
    ReviewsResponse,
    SearchItem,
    SearchResponse,
    Seller,
    SellerResponse,
    SpecificationGroup,
    Store,
    StoreHours,
    StoreResponse,
    StoreService,
    Suggestion,
    Variant,
    Video,
    Warranty,
)
from scrapebadger.walmart.products import ProductsClient
from scrapebadger.walmart.reference import ReferenceClient
from scrapebadger.walmart.search import SearchClient
from scrapebadger.walmart.sellers import SellersClient
from scrapebadger.walmart.stores import StoresClient

__all__ = [
    "AutocompleteResponse",
    "Badge",
    "Breadcrumb",
    "ConditionOffer",
    "EmbeddedSeller",
    "FulfillmentOption",
    "FulfillmentSummary",
    "Image",
    "LocationContext",
    "Market",
    "MarketsResponse",
    "NameValue",
    "NutritionFacts",
    "Price",
    "PriceInfo",
    "PriceRange",
    "Product",
    "ProductsClient",
    "Promotion",
    "RatingDistribution",
    "ReferenceClient",
    "ReturnPolicy",
    "Review",
    "ReviewsResponse",
    "SearchClient",
    "SearchItem",
    "SearchResponse",
    "Seller",
    "SellerResponse",
    "SellersClient",
    "SpecificationGroup",
    "Store",
    "StoreHours",
    "StoreResponse",
    "StoreService",
    "StoresClient",
    "Suggestion",
    "Variant",
    "Video",
    "WalmartClient",
    "Warranty",
]
