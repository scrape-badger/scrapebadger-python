"""Leboncoin API module for ScrapeBadger SDK.

This module provides a comprehensive async client for scraping Leboncoin data
through the ScrapeBadger API. All methods are async and return strongly-typed
Pydantic models.

Example:
    ```python
    from scrapebadger import ScrapeBadger

    async with ScrapeBadger(api_key="your-key") as client:
        # Search for ads
        results = await client.leboncoin.search.search("velo")
        for ad in results.ads:
            print(f"{ad.subject}: {ad.price_eur}")

        # Get ad detail
        detail = await client.leboncoin.ads.get_ad(2812345678)
        print(detail.ad.subject)

        # Get a seller profile
        seller = await client.leboncoin.sellers.get_seller("12345678")
        print(f"{seller.seller.name}: {seller.seller.total_ads} ads")
    ```
"""

from scrapebadger.leboncoin.client import LeboncoinClient
from scrapebadger.leboncoin.models import (
    Ad,
    AdResponse,
    Attribute,
    CategoriesResponse,
    Category,
    Department,
    DepartmentsResponse,
    FeedbackScores,
    Images,
    Location,
    LocationSearchResponse,
    LocationSuggestion,
    MarketsResponse,
    Owner,
    Region,
    RegionsResponse,
    SearchResponse,
    Seller,
    SellerListingsResponse,
    SellerResponse,
    SimilarResponse,
    StoreRatingReview,
)

__all__ = [
    # Ad
    "Ad",
    "AdResponse",
    "Attribute",
    # Reference
    "CategoriesResponse",
    "Category",
    "Department",
    "DepartmentsResponse",
    # Seller
    "FeedbackScores",
    # Shared
    "Images",
    # Client
    "LeboncoinClient",
    "Location",
    "LocationSearchResponse",
    "LocationSuggestion",
    "MarketsResponse",
    "Owner",
    "Region",
    "RegionsResponse",
    # Search
    "SearchResponse",
    "Seller",
    "SellerListingsResponse",
    "SellerResponse",
    "SimilarResponse",
    "StoreRatingReview",
]
