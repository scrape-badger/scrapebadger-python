"""Pydantic models for Amazon API responses.

These models mirror the backend ``amazon_scraper`` response schema field-for-field.
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


class AmazonPrice(_BaseModel):
    """A parsed price with both the numeric value and its raw rendering."""

    value: float | None = None
    currency: str | None = None
    symbol: str | None = None
    raw: str | None = None


class Pagination(_BaseModel):
    """Page-number pagination (Amazon listings use 1-based page numbers)."""

    current_page: int = 1
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


class CategoryInfo(_BaseModel):
    """A reference category / department alias (for /categories)."""

    name: str
    alias: str
    search_alias: str | None = None
    bestseller_node: str | None = None


# =============================================================================
# Product Models (/products/{asin})
# =============================================================================


class RatingBreakdown(_BaseModel):
    """Per-star rating distribution (percentages 0-100)."""

    five_star: int | None = None
    four_star: int | None = None
    three_star: int | None = None
    two_star: int | None = None
    one_star: int | None = None


class BestsellersRankEntry(_BaseModel):
    """A single bestsellers-rank entry for a product."""

    rank: int | None = None
    category: str | None = None
    link: str | None = None


class ProductVariant(_BaseModel):
    """A buying option / variation of a product."""

    asin: str
    attributes: dict[str, str] = Field(default_factory=dict)
    price: AmazonPrice | None = None
    is_current: bool = False


class Buybox(_BaseModel):
    """The featured-offer (buybox) winner shown on the product page."""

    seller_name: str | None = None
    seller_id: str | None = None
    price: AmazonPrice | None = None
    fulfillment: str | None = None


class ProductBadges(_BaseModel):
    """Promotional badges attached to a product."""

    amazons_choice: bool = False
    amazons_choice_keyword: str | None = None
    best_seller: bool = False
    prime: bool = False
    climate_pledge_friendly: bool = False


class Coupon(_BaseModel):
    """A clippable coupon on the product page."""

    text: str | None = None
    discount: str | None = None


class ProductDeal(_BaseModel):
    """A deal active on the product page."""

    type: str | None = None
    price: AmazonPrice | None = None
    ends_at: str | None = None


class Delivery(_BaseModel):
    """Delivery information shown on the product page."""

    message: str | None = None
    date: str | None = None
    is_free: bool | None = None


class RelatedProduct(_BaseModel):
    """A related product (frequently-bought-together / also-bought)."""

    asin: str
    title: str | None = None
    link: str | None = None
    image: str | None = None
    price: AmazonPrice | None = None


class Product(_BaseModel):
    """Full product detail (PDP)."""

    asin: str
    parent_asin: str | None = None
    title: str | None = None
    link: str | None = None
    brand: str | None = None
    brand_url: str | None = None
    manufacturer: str | None = None
    model_number: str | None = None
    price: AmazonPrice | None = None
    list_price: AmazonPrice | None = None
    savings_amount: AmazonPrice | None = None
    discount_percent: float | None = None
    rating: float | None = None
    ratings_total: int | None = None
    rating_breakdown: RatingBreakdown | None = None
    bought_past_month: str | None = None
    in_stock: bool | None = None
    availability: str | None = None
    feature_bullets: list[str] = Field(default_factory=list)
    description: str | None = None
    main_image: str | None = None
    images: list[str] = Field(default_factory=list)
    images_count: int = 0
    videos: list[str] = Field(default_factory=list)
    videos_count: int = 0
    has_aplus_content: bool = False
    variants: list[ProductVariant] = Field(default_factory=list)
    variant_asins: list[str] = Field(default_factory=list)
    categories: list[str] = Field(default_factory=list)
    bestsellers_rank: list[BestsellersRankEntry] = Field(default_factory=list)
    attributes: dict[str, str] = Field(default_factory=dict)
    specifications: dict[str, str] = Field(default_factory=dict)
    dimensions: str | None = None
    weight: str | None = None
    first_available: str | None = None
    country_of_origin: str | None = None
    buybox: Buybox | None = None
    sold_by: str | None = None
    ships_from: str | None = None
    fulfilled_by: str | None = None
    is_amazon_seller: bool | None = None
    badges: ProductBadges = Field(default_factory=ProductBadges)
    coupon: Coupon | None = None
    deal: ProductDeal | None = None
    delivery: Delivery | None = None
    frequently_bought_together: list[RelatedProduct] = Field(default_factory=list)
    also_bought: list[RelatedProduct] = Field(default_factory=list)
    answered_questions: int | None = None
    top_reviews: list[Review] = Field(default_factory=list)
    scraped_utc: float | None = None
    scraped_at: str | None = None


# =============================================================================
# Search Models (/search)
# =============================================================================


class SearchResult(_BaseModel):
    """A single search / category-browse result row."""

    position: int
    asin: str
    title: str | None = None
    link: str | None = None
    image: str | None = None
    price: AmazonPrice | None = None
    list_price: AmazonPrice | None = None
    unit_price: str | None = None
    rating: float | None = None
    ratings_total: int | None = None
    is_prime: bool = False
    is_sponsored: bool = False
    is_amazons_choice: bool = False
    is_best_seller: bool = False
    bought_past_month: str | None = None
    coupon: str | None = None
    availability: str | None = None


# =============================================================================
# Offer Models (/products/{asin}/offers)
# =============================================================================


class OfferSeller(_BaseModel):
    """The seller behind a specific offer."""

    name: str | None = None
    id: str | None = None
    link: str | None = None
    rating: float | None = None
    ratings_total: int | None = None
    ratings_percentage_positive: int | None = None


class OfferCondition(_BaseModel):
    """The condition of an offered item."""

    is_new: bool | None = None
    title: str | None = None
    comments: str | None = None


class OfferDelivery(_BaseModel):
    """Delivery terms for a specific offer."""

    is_free: bool | None = None
    fulfilled_by_amazon: bool | None = None
    date: str | None = None
    price: AmazonPrice | None = None


class Offer(_BaseModel):
    """A single seller offer for a product."""

    position: int
    seller: OfferSeller | None = None
    price: AmazonPrice | None = None
    condition: OfferCondition | None = None
    delivery: OfferDelivery | None = None
    buybox_winner: bool = False
    is_prime: bool = False
    minimum_order_quantity: int | None = None
    maximum_order_quantity: int | None = None


# =============================================================================
# Review Models (/products/{asin}/reviews)
# =============================================================================


class ReviewProfile(_BaseModel):
    """The reviewer's public profile."""

    name: str | None = None
    link: str | None = None
    id: str | None = None
    image: str | None = None


class Review(_BaseModel):
    """A single product review."""

    id: str | None = None
    title: str | None = None
    body: str | None = None
    rating: float | None = None
    date_raw: str | None = None
    date_utc: float | None = None
    date_at: str | None = None
    review_country: str | None = None
    is_global_review: bool = False
    profile: ReviewProfile | None = None
    verified_purchase: bool = False
    vine_program: bool = False
    helpful_votes: int | None = None
    variant: str | None = None
    images: list[str] = Field(default_factory=list)


# =============================================================================
# Bestseller / New-release Models (/bestsellers, /new-releases)
# =============================================================================


class Bestseller(_BaseModel):
    """A single bestseller / new-release row."""

    rank: int | None = None
    position: int
    asin: str
    title: str | None = None
    link: str | None = None
    image: str | None = None
    rating: float | None = None
    ratings_total: int | None = None
    price: AmazonPrice | None = None


# =============================================================================
# Deal Models (/deals)
# =============================================================================


class Deal(_BaseModel):
    """A single deal row."""

    position: int
    asin: str
    title: str | None = None
    link: str | None = None
    image: str | None = None
    deal_price: AmazonPrice | None = None
    list_price: AmazonPrice | None = None
    discount_percent: float | None = None
    deal_type: str | None = None
    is_lightning_deal: bool = False
    badge: str | None = None
    ends_at_utc: float | None = None
    ends_at: str | None = None


# =============================================================================
# Seller Models (/sellers/{seller_id})
# =============================================================================


class FeedbackWindow(_BaseModel):
    """Feedback counts for a single rolling window."""

    positive: int | None = None
    neutral: int | None = None
    negative: int | None = None
    count: int | None = None


class SellerFeedbackSummary(_BaseModel):
    """Seller feedback summary across rolling windows.

    The ``twelve_month``, ``ninety_day`` and ``thirty_day`` fields are also
    accessible under the wire aliases ``12mo``, ``90d`` and ``30d``.
    """

    lifetime: FeedbackWindow | None = None
    twelve_month: FeedbackWindow | None = Field(default=None, alias="12mo")
    ninety_day: FeedbackWindow | None = Field(default=None, alias="90d")
    thirty_day: FeedbackWindow | None = Field(default=None, alias="30d")


class Seller(_BaseModel):
    """A seller profile."""

    seller_id: str
    name: str | None = None
    link: str | None = None
    rating: float | None = None
    ratings_total: int | None = None
    ratings_percentage_positive: int | None = None
    feedback: SellerFeedbackSummary | None = None
    business_name: str | None = None
    business_address: str | None = None
    member_since: str | None = None


class SellerFeedbackEntry(_BaseModel):
    """A single buyer-feedback entry for a seller."""

    rating: float | None = None
    comment: str | None = None
    rater: str | None = None
    date_raw: str | None = None
    date_utc: float | None = None
    date_at: str | None = None


# =============================================================================
# Autocomplete Models (/autocomplete)
# =============================================================================


class AutocompleteSuggestion(_BaseModel):
    """A single keyword suggestion."""

    value: str
    alias: str | None = None


# =============================================================================
# Response Envelopes
# =============================================================================


class SearchResponse(_BaseModel):
    """Response from the /search endpoint."""

    query: str
    domain: str
    results: list[SearchResult] = Field(default_factory=list)
    pagination: Pagination = Field(default_factory=Pagination)
    scraped_utc: float | None = None
    scraped_at: str | None = None


class ProductDetailResponse(_BaseModel):
    """Response from the /products/{asin} endpoint."""

    domain: str
    product: Product


class OffersResponse(_BaseModel):
    """Response from the /products/{asin}/offers endpoint."""

    asin: str
    domain: str
    buybox: Offer | None = None
    offers: list[Offer] = Field(default_factory=list)
    total_offers: int | None = None
    scraped_utc: float | None = None
    scraped_at: str | None = None


class ReviewsResponse(_BaseModel):
    """Response from the /products/{asin}/reviews endpoint."""

    asin: str
    domain: str
    reviews: list[Review] = Field(default_factory=list)
    rating: float | None = None
    ratings_total: int | None = None
    rating_breakdown: RatingBreakdown | None = None
    pagination: Pagination = Field(default_factory=Pagination)
    scraped_utc: float | None = None
    scraped_at: str | None = None


class BestsellersResponse(_BaseModel):
    """Response from the /bestsellers endpoint."""

    domain: str
    category: str | None = None
    bestsellers: list[Bestseller] = Field(default_factory=list)
    pagination: Pagination = Field(default_factory=Pagination)
    scraped_utc: float | None = None
    scraped_at: str | None = None


class NewReleasesResponse(_BaseModel):
    """Response from the /new-releases endpoint."""

    domain: str
    category: str | None = None
    new_releases: list[Bestseller] = Field(default_factory=list)
    pagination: Pagination = Field(default_factory=Pagination)
    scraped_utc: float | None = None
    scraped_at: str | None = None


class DealsResponse(_BaseModel):
    """Response from the /deals endpoint."""

    domain: str
    category: str | None = None
    deals: list[Deal] = Field(default_factory=list)
    pagination: Pagination = Field(default_factory=Pagination)
    scraped_utc: float | None = None
    scraped_at: str | None = None


class CategoryResponse(_BaseModel):
    """Response from the /category endpoint."""

    domain: str
    node: str
    results: list[SearchResult] = Field(default_factory=list)
    pagination: Pagination = Field(default_factory=Pagination)
    scraped_utc: float | None = None
    scraped_at: str | None = None


class SellerProfileResponse(_BaseModel):
    """Response from the /sellers/{seller_id} endpoint."""

    domain: str
    seller: Seller


class SellerProductsResponse(_BaseModel):
    """Response from the /sellers/{seller_id}/products endpoint."""

    domain: str
    seller_id: str
    products: list[SearchResult] = Field(default_factory=list)
    pagination: Pagination = Field(default_factory=Pagination)
    scraped_utc: float | None = None
    scraped_at: str | None = None


class SellerFeedbackResponse(_BaseModel):
    """Response from the /sellers/{seller_id}/feedback endpoint."""

    domain: str
    seller_id: str
    feedback: list[SellerFeedbackEntry] = Field(default_factory=list)
    pagination: Pagination = Field(default_factory=Pagination)
    scraped_utc: float | None = None
    scraped_at: str | None = None


class AutocompleteResponse(_BaseModel):
    """Response from the /autocomplete endpoint."""

    query: str
    domain: str
    suggestions: list[AutocompleteSuggestion] = Field(default_factory=list)


class MarketsResponse(_BaseModel):
    """Response from the /markets endpoint."""

    markets: list[MarketInfo] = Field(default_factory=list)


class CategoriesResponse(_BaseModel):
    """Response from the /categories endpoint."""

    categories: list[CategoryInfo] = Field(default_factory=list)
