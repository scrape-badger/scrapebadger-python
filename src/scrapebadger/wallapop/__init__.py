"""Wallapop API module for ScrapeBadger SDK.

This module provides an async client for scraping the Wallapop second-hand
marketplace (Spain, Italy, Portugal) through the ScrapeBadger API. All methods
are async and return strongly-typed Pydantic models.

Example:
    ```python
    from scrapebadger import ScrapeBadger

    async with ScrapeBadger(api_key="your-key") as client:
        # Search listings
        results = await client.wallapop.search("iphone 14", max_price=400)
        for item in results.items:
            print(f"{item.title} — {item.price} {item.currency}")

        # Get listing detail
        item = await client.wallapop.get_item("nzxeknm5x562")
        print(item.title, item.views)

        # Get a seller profile
        user = await client.wallapop.get_user("alexc-25115753")
        print(user.name, user.rating_average)
    ```
"""

from scrapebadger.wallapop.client import WallapopClient
from scrapebadger.wallapop.models import (
    Attribute,
    AutocompleteResponse,
    CategoriesResponse,
    Category,
    FilterOption,
    FilterOptionsResponse,
    FiltersResponse,
    Image,
    ItemDetail,
    Location,
    Market,
    MarketsResponse,
    Review,
    Reviewer,
    ReviewItem,
    ReviewsResponse,
    SearchFilter,
    SearchItem,
    SearchResponse,
    Suggestion,
    TaxonomyNode,
    UserItem,
    UserItemsResponse,
    UserProfile,
    UserValidations,
)

__all__ = [
    # Shared
    "Attribute",
    # Reference
    "AutocompleteResponse",
    "CategoriesResponse",
    "Category",
    "FilterOption",
    "FilterOptionsResponse",
    "FiltersResponse",
    "Image",
    # Item detail
    "ItemDetail",
    "Location",
    "Market",
    "MarketsResponse",
    # Users
    "Review",
    "ReviewItem",
    "Reviewer",
    "ReviewsResponse",
    "SearchFilter",
    # Search
    "SearchItem",
    "SearchResponse",
    "Suggestion",
    "TaxonomyNode",
    "UserItem",
    "UserItemsResponse",
    "UserProfile",
    "UserValidations",
    # Client
    "WallapopClient",
]
