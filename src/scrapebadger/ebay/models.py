"""Pydantic models for eBay API responses.

These models mirror the backend ``ebay_scraper`` response schema field-for-field.
All models are immutable (frozen) and ignore unknown fields for forward
compatibility. Every datetime field ships in BOTH ``*_utc`` (Unix float) and
``*_at`` (ISO-8601 Z string).
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

# =============================================================================
# Base Configuration
# =============================================================================


class _BaseModel(BaseModel):
    """Base model with common configuration."""

    model_config = ConfigDict(
        frozen=True,
        populate_by_name=True,
        extra="ignore",
    )


# =============================================================================
# Shared Models
# =============================================================================


class EbayPrice(_BaseModel):
    """A parsed price with both the numeric value and its raw rendering."""

    value: float | None = None
    currency: str | None = None
    symbol: str | None = None
    raw: str | None = None


class Pagination(_BaseModel):
    """Page-number pagination (eBay listings use 1-based ``_pgn`` numbers)."""

    current_page: int = 1
    per_page: int | None = None
    total_pages: int | None = None
    total_results: int | None = None


class MarketInfo(_BaseModel):
    """A single supported marketplace (for /markets)."""

    code: str
    domain: str
    country: str
    currency: str
    locale: str
    name: str
    site_id: int


class CategoryInfo(_BaseModel):
    """A reference category alias (for /categories)."""

    name: str
    category_id: str
    parent: str | None = None


class EbayImage(_BaseModel):
    """A single image with optional dimensions."""

    url: str
    width: int | None = None
    height: int | None = None


class ShippingOption(_BaseModel):
    """A single shipping option (per-destination rate from JSON-LD or DOM)."""

    cost: EbayPrice | None = None
    is_free: bool | None = None
    service: str | None = None
    destination_country: str | None = None
    delivery_estimate: str | None = None


# =============================================================================
# Search / listings (cards)
# =============================================================================


class SearchResult(_BaseModel):
    """One eBay search/listing card (search, seller items, category, sold)."""

    position: int
    item_id: str | None = None
    product_id: str | None = None
    title: str | None = None
    url: str | None = None
    image: str | None = None
    price: EbayPrice | None = None
    original_price: EbayPrice | None = None
    discount_percent: float | None = None
    currency: str | None = None
    condition: str | None = None
    brand: str | None = None
    buying_format: str | None = None  # "Buy It Now" | "Auction" | "Best Offer"
    is_auction: bool = False
    bids: int | None = None
    current_bid: EbayPrice | None = None  # auctions: the current high bid (mirrors ``price``)
    time_left: str | None = None  # relative remaining, e.g. "12h 16m" / "4d 8h"
    shipping: str | None = None
    shipping_cost: EbayPrice | None = None
    free_shipping: bool | None = None
    location: str | None = None
    returns: str | None = None
    sold_count: int | None = None
    sold_date: str | None = None  # completed cards: sale date as rendered, e.g. "2 Jul 2026"
    sold_date_at: str | None = None  # ISO "2026-07-02", best-effort (None on non-English markets)
    watchers: int | None = None
    coupon: str | None = None
    rating: float | None = None
    ratings_total: int | None = None
    seller_name: str | None = None
    seller_feedback_percent: float | None = None
    seller_feedback_score: int | None = None
    program_badge: str | None = None  # e.g. "eBay Refurbished"
    is_sponsored: bool = False


# =============================================================================
# Item detail (/items/{item_id})
# =============================================================================


class ItemSeller(_BaseModel):
    """The seller summary embedded in an item detail."""

    username: str | None = None
    url: str | None = None
    feedback_score: int | None = None
    feedback_percent: float | None = None
    store_name: str | None = None
    store_url: str | None = None


class ReturnsPolicy(_BaseModel):
    """The returns policy of a listing."""

    accepted: bool | None = None
    period: str | None = None  # e.g. "30 days"
    cost_paid_by: str | None = None  # "buyer" | "seller"
    raw: str | None = None


class Item(_BaseModel):
    """Full detail for a single eBay listing (/items/{item_id})."""

    item_id: str
    product_id: str | None = None
    legacy_item_id: str | None = None
    title: str | None = None
    subtitle: str | None = None
    url: str | None = None
    condition: str | None = None
    condition_id: str | None = None
    condition_description: str | None = None
    price: EbayPrice | None = None
    original_price: EbayPrice | None = None
    discount_percent: float | None = None
    currency: str | None = None
    availability: str | None = None
    quantity_available: int | None = None
    quantity_sold: int | None = None
    watchers: int | None = None
    buying_format: str | None = None
    is_auction: bool = False
    bids: int | None = None
    current_bid: EbayPrice | None = None  # auctions: the current high bid (mirrors ``price``)
    time_left: str | None = None  # relative remaining, e.g. "12h 16m"
    is_ended: bool = False  # listing has closed (sold / ended), any buying format
    end_time_utc: float | None = None  # listing end: auction close / sold time (Unix float)
    end_time_at: str | None = None  # listing end: auction close / sold time (ISO-8601 Z)
    buy_it_now_price: EbayPrice | None = None  # BIN price (fixed-price, or auction-with-BIN)
    best_offer_enabled: bool | None = None
    brand: str | None = None
    mpn: str | None = None
    model: str | None = None
    color: str | None = None
    gtin: str | None = None
    main_image: str | None = None
    images: list[EbayImage] = Field(default_factory=list)
    images_count: int = 0
    description: str | None = None
    seller_notes: str | None = None
    item_specifics: dict[str, str] = Field(default_factory=dict)
    categories: list[str] = Field(default_factory=list)
    category_id: str | None = None
    shipping_options: list[ShippingOption] = Field(default_factory=list)
    shipping_cost: EbayPrice | None = None
    free_shipping: bool | None = None
    item_location: str | None = None
    ships_to: list[str] = Field(default_factory=list)
    returns: ReturnsPolicy | None = None
    seller: ItemSeller | None = None
    rating: float | None = None
    ratings_total: int | None = None
    date_modified_utc: float | None = None
    date_modified_at: str | None = None
    scraped_utc: float | None = None
    scraped_at: str | None = None


# =============================================================================
# Seller profile (/sellers/{username})
# =============================================================================


class FeedbackBreakdown(_BaseModel):
    """Positive/neutral/negative feedback counts over a window."""

    positive: int | None = None
    neutral: int | None = None
    negative: int | None = None


class Seller(_BaseModel):
    """An eBay seller's public profile (/sellers/{username})."""

    username: str
    url: str | None = None
    store_name: str | None = None
    store_url: str | None = None
    feedback_score: int | None = None
    feedback_percent: float | None = None
    member_since: str | None = None
    location: str | None = None
    items_for_sale: int | None = None
    feedback_12mo: FeedbackBreakdown | None = None
    top_rated: bool | None = None
    scraped_utc: float | None = None
    scraped_at: str | None = None


class FeedbackEntry(_BaseModel):
    """A single buyer feedback comment on a seller."""

    rating: str | None = None  # "positive" | "neutral" | "negative"
    comment: str | None = None
    rater: str | None = None
    item: str | None = None
    date_raw: str | None = None
    date_utc: float | None = None
    date_at: str | None = None


# =============================================================================
# Reviews (/items/{item_id}/reviews)
# =============================================================================


class RatingHistogram(_BaseModel):
    """Star-rating histogram for a catalog product."""

    five_star: int | None = None
    four_star: int | None = None
    three_star: int | None = None
    two_star: int | None = None
    one_star: int | None = None


class Review(_BaseModel):
    """A single catalog product review."""

    title: str | None = None
    body: str | None = None
    rating: float | None = None
    author: str | None = None
    date_raw: str | None = None
    date_utc: float | None = None
    date_at: str | None = None
    helpful_votes: int | None = None
    verified_purchase: bool = False


# =============================================================================
# Autocomplete
# =============================================================================


class AutocompleteSuggestion(_BaseModel):
    """A single autocomplete suggestion."""

    value: str


# =============================================================================
# Response envelopes
# =============================================================================


class SearchResponse(_BaseModel):
    """Response for /search and /completed."""

    query: str | None = None
    domain: str
    category_id: str | None = None
    sold: bool = False
    results: list[SearchResult] = Field(default_factory=list)
    facets: dict[str, list[str]] = Field(default_factory=dict)
    pagination: Pagination = Field(default_factory=Pagination)
    scraped_utc: float | None = None
    scraped_at: str | None = None


class ItemDetailResponse(_BaseModel):
    """Response for /items/{item_id}."""

    domain: str
    item: Item


class SellerProfileResponse(_BaseModel):
    """Response for /sellers/{username}."""

    domain: str
    seller: Seller


class SellerItemsResponse(_BaseModel):
    """Response for /sellers/{username}/items."""

    domain: str
    username: str
    results: list[SearchResult] = Field(default_factory=list)
    pagination: Pagination = Field(default_factory=Pagination)
    scraped_utc: float | None = None
    scraped_at: str | None = None


class SellerFeedbackResponse(_BaseModel):
    """Response for /sellers/{username}/feedback."""

    domain: str
    username: str
    feedback: list[FeedbackEntry] = Field(default_factory=list)
    pagination: Pagination = Field(default_factory=Pagination)
    scraped_utc: float | None = None
    scraped_at: str | None = None


class ReviewsResponse(_BaseModel):
    """Response for /items/{item_id}/reviews."""

    domain: str
    item_id: str | None = None
    product_id: str | None = None
    rating: float | None = None
    ratings_total: int | None = None
    histogram: RatingHistogram | None = None
    reviews: list[Review] = Field(default_factory=list)
    pagination: Pagination = Field(default_factory=Pagination)
    scraped_utc: float | None = None
    scraped_at: str | None = None


class CategoryResponse(_BaseModel):
    """Response for /categories/{category_id}/items."""

    domain: str
    category_id: str
    results: list[SearchResult] = Field(default_factory=list)
    facets: dict[str, list[str]] = Field(default_factory=dict)
    pagination: Pagination = Field(default_factory=Pagination)
    scraped_utc: float | None = None
    scraped_at: str | None = None


class AutocompleteResponse(_BaseModel):
    """Response for /autocomplete."""

    query: str
    domain: str
    suggestions: list[AutocompleteSuggestion] = Field(default_factory=list)


class MarketsResponse(_BaseModel):
    """Response for /markets."""

    markets: list[MarketInfo] = Field(default_factory=list)


class CategoriesResponse(_BaseModel):
    """Response for /categories."""

    categories: list[CategoryInfo] = Field(default_factory=list)
