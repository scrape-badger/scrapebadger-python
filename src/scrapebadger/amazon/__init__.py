"""Amazon API module for ScrapeBadger SDK.

This module provides a comprehensive async client for scraping Amazon data
through the ScrapeBadger API. All methods are async and return strongly-typed
Pydantic models.

Example:
    ```python
    from scrapebadger import ScrapeBadger

    async with ScrapeBadger(api_key="your-key") as client:
        # Search for products
        results = await client.amazon.search.search("wireless headphones")
        for item in results.results:
            print(f"{item.position}. {item.title}")

        # Get product detail
        detail = await client.amazon.products.get("B08N5WRWNW")
        print(detail.product.title)

        # Get a seller profile
        seller = await client.amazon.sellers.get("A2L77EE7U53NWQ")
        print(f"{seller.seller.name}: {seller.seller.rating}*")
    ```
"""

from scrapebadger.amazon.client import AmazonClient
from scrapebadger.amazon.models import (
    AmazonPrice,
    AutocompleteResponse,
    AutocompleteSuggestion,
    Bestseller,
    BestsellersRankEntry,
    BestsellersResponse,
    Buybox,
    CategoriesResponse,
    CategoryInfo,
    CategoryResponse,
    Coupon,
    Deal,
    DealsResponse,
    Delivery,
    FeedbackWindow,
    MarketInfo,
    MarketsResponse,
    NewReleasesResponse,
    Offer,
    OfferCondition,
    OfferDelivery,
    OfferSeller,
    OffersResponse,
    Pagination,
    Product,
    ProductBadges,
    ProductDeal,
    ProductDetailResponse,
    ProductVariant,
    RatingBreakdown,
    RelatedProduct,
    Review,
    ReviewProfile,
    ReviewsResponse,
    SearchResponse,
    SearchResult,
    Seller,
    SellerFeedbackEntry,
    SellerFeedbackResponse,
    SellerFeedbackSummary,
    SellerProductsResponse,
    SellerProfileResponse,
)

__all__ = [
    # Client
    "AmazonClient",
    # Shared models
    "AmazonPrice",
    # Autocomplete
    "AutocompleteResponse",
    "AutocompleteSuggestion",
    # Bestsellers / new releases
    "Bestseller",
    "BestsellersRankEntry",
    "BestsellersResponse",
    "Buybox",
    # Reference
    "CategoriesResponse",
    "CategoryInfo",
    "CategoryResponse",
    "Coupon",
    # Deals
    "Deal",
    "DealsResponse",
    "Delivery",
    "FeedbackWindow",
    "MarketInfo",
    "MarketsResponse",
    "NewReleasesResponse",
    # Offers
    "Offer",
    "OfferCondition",
    "OfferDelivery",
    "OfferSeller",
    "OffersResponse",
    "Pagination",
    # Product
    "Product",
    "ProductBadges",
    "ProductDeal",
    "ProductDetailResponse",
    "ProductVariant",
    "RatingBreakdown",
    "RelatedProduct",
    # Reviews
    "Review",
    "ReviewProfile",
    "ReviewsResponse",
    # Search
    "SearchResponse",
    "SearchResult",
    # Sellers
    "Seller",
    "SellerFeedbackEntry",
    "SellerFeedbackResponse",
    "SellerFeedbackSummary",
    "SellerProductsResponse",
    "SellerProfileResponse",
]
