"""Gumtree API module for ScrapeBadger SDK.

This module provides an async client for scraping Gumtree classifieds through
the ScrapeBadger API: gumtree.com (``market="uk"``, the default),
gumtree.com.au (``"au"``) and gumtree.co.za (``"za"``). All methods are async
and return strongly-typed Pydantic models.

Example:
    ```python
    from scrapebadger import ScrapeBadger

    async with ScrapeBadger(api_key="your-key") as client:
        # Search
        results = await client.gumtree.search("mountain bike", category="bicycles")
        for listing in results.listings:
            print(listing.title, listing.price_text)

        # Listing detail
        detail = await client.gumtree.get_listing("1803293391")
        print(detail.title, detail.seller.name if detail.seller else None)

        # Australia and South Africa take numeric category / location ids
        au = await client.gumtree.search("road bike", market="au", location="3003435")
        za = await client.gumtree.search(market="za", category="9077", location="3100003")
    ```
"""

from scrapebadger.gumtree.client import GumtreeClient, GumtreeMarket
from scrapebadger.gumtree.models import (
    Attribute,
    AutocompleteResponse,
    Breadcrumb,
    CategoryFacet,
    CategoryRef,
    FilterOption,
    FiltersResponse,
    ListingDetail,
    ListingSummary,
    LocationAutocompleteResponse,
    LocationSuggestion,
    MarketInfo,
    MarketsResponse,
    SearchFilter,
    SearchResponse,
    Seller,
    SellerListingsResponse,
    SellerRating,
    SellerVerification,
    SortOption,
    Suggestion,
    TreeNode,
    TreeResponse,
)

__all__ = [
    "Attribute",
    "AutocompleteResponse",
    "Breadcrumb",
    "CategoryFacet",
    "CategoryRef",
    "FilterOption",
    "FiltersResponse",
    "GumtreeClient",
    "GumtreeMarket",
    "ListingDetail",
    "ListingSummary",
    "LocationAutocompleteResponse",
    "LocationSuggestion",
    "MarketInfo",
    "MarketsResponse",
    "SearchFilter",
    "SearchResponse",
    "Seller",
    "SellerListingsResponse",
    "SellerRating",
    "SellerVerification",
    "SortOption",
    "Suggestion",
    "TreeNode",
    "TreeResponse",
]
