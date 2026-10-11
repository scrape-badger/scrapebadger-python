"""Gumtree API module for ScrapeBadger SDK.

This module provides an async client for scraping gumtree.com (United Kingdom)
classifieds through the ScrapeBadger API. All methods are async and return
strongly-typed Pydantic models. Gumtree is UK-only, so no method takes a
market/country parameter.

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
    ```
"""

from scrapebadger.gumtree.client import GumtreeClient
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
    "ListingDetail",
    "ListingSummary",
    "LocationAutocompleteResponse",
    "LocationSuggestion",
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
