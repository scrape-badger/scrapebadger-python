"""Vinted API module for ScrapeBadger SDK.

This module provides a comprehensive async client for scraping Vinted data
through the ScrapeBadger API. All methods are async and return strongly-typed
Pydantic models.

Example:
    ```python
    from scrapebadger import ScrapeBadger

    async with ScrapeBadger(api_key="your-key") as client:
        # Search for items
        results = await client.vinted.search.search("nike air max")
        for item in results.items:
            print(f"{item.title}: {item.price.amount} {item.price.currency_code}")

        # Get item details
        detail = await client.vinted.items.get(123456789)
        print(detail.item.description)

        # Get user profile
        profile = await client.vinted.users.get_profile(12345)
        print(f"{profile.user.login}: {profile.user.item_count} items")
    ```
"""

from scrapebadger.vinted.client import VintedClient
from scrapebadger.vinted.models import (
    BrandsResponse,
    ColorsResponse,
    ItemDetailResponse,
    MarketsResponse,
    SearchResponse,
    StatusesResponse,
    UserItemsResponse,
    UserProfileResponse,
    VintedBrand,
    VintedColor,
    VintedItemDetail,
    VintedItemSummary,
    VintedMarket,
    VintedPagination,
    VintedPhoto,
    VintedPrice,
    VintedSellerSummary,
    VintedStatus,
    VintedUserProfile,
    VintedUserSummary,
)

__all__ = [
    # Response envelopes
    "BrandsResponse",
    "ColorsResponse",
    "ItemDetailResponse",
    "MarketsResponse",
    "SearchResponse",
    "StatusesResponse",
    "UserItemsResponse",
    "UserProfileResponse",
    # Reference models
    "VintedBrand",
    # Client
    "VintedClient",
    "VintedColor",
    # Core models
    "VintedItemDetail",
    "VintedItemSummary",
    "VintedMarket",
    # Pagination
    "VintedPagination",
    # Nested models
    "VintedPhoto",
    "VintedPrice",
    "VintedSellerSummary",
    "VintedStatus",
    "VintedUserProfile",
    "VintedUserSummary",
]
