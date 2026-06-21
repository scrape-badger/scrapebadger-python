"""eBay API module for ScrapeBadger SDK.

This module provides a comprehensive async client for scraping eBay data
through the ScrapeBadger API. All methods are async and return strongly-typed
Pydantic models.

Example:
    ```python
    from scrapebadger import ScrapeBadger

    async with ScrapeBadger(api_key="your-key") as client:
        # Search for listings
        results = await client.ebay.search.search("nintendo switch")
        for item in results.results:
            print(f"{item.position}. {item.title}")

        # Get item detail
        detail = await client.ebay.items.get_item("123456789012")
        print(detail.item.title)

        # Get a seller profile
        seller = await client.ebay.sellers.get_seller("musicmagpie")
        print(f"{seller.seller.username}: {seller.seller.feedback_percent}%")
    ```
"""

from scrapebadger.ebay.client import EbayClient
from scrapebadger.ebay.models import (
    AutocompleteResponse,
    AutocompleteSuggestion,
    CategoriesResponse,
    CategoryInfo,
    CategoryResponse,
    EbayImage,
    EbayPrice,
    FeedbackBreakdown,
    FeedbackEntry,
    Item,
    ItemDetailResponse,
    ItemSeller,
    MarketInfo,
    MarketsResponse,
    Pagination,
    RatingHistogram,
    ReturnsPolicy,
    Review,
    ReviewsResponse,
    SearchResponse,
    SearchResult,
    Seller,
    SellerFeedbackResponse,
    SellerItemsResponse,
    SellerProfileResponse,
    ShippingOption,
)

__all__ = [
    # Autocomplete
    "AutocompleteResponse",
    "AutocompleteSuggestion",
    # Reference
    "CategoriesResponse",
    "CategoryInfo",
    "CategoryResponse",
    # Client
    "EbayClient",
    # Shared
    "EbayImage",
    "EbayPrice",
    # Sellers
    "FeedbackBreakdown",
    "FeedbackEntry",
    # Item
    "Item",
    "ItemDetailResponse",
    "ItemSeller",
    "MarketInfo",
    "MarketsResponse",
    "Pagination",
    # Reviews
    "RatingHistogram",
    "ReturnsPolicy",
    "Review",
    "ReviewsResponse",
    # Search
    "SearchResponse",
    "SearchResult",
    "Seller",
    "SellerFeedbackResponse",
    "SellerItemsResponse",
    "SellerProfileResponse",
    "ShippingOption",
]
