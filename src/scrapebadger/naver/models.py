"""Pydantic models for Naver API responses.

These models mirror the backend ``naver_scraper`` response schema. All models
are immutable (frozen) and ignore unknown fields for forward compatibility.

Naver is a Korean portal and commerce platform: a single host set
(naver.com) is scraped, so no model carries a market/country selector.
Deeply nested or upstream "union" card shapes (finder/listing product cards,
Shopping Live products, full product detail) are surfaced as
``dict[str, Any]`` to preserve every field the upstream returns without
pinning a schema the backend documents as open-ended.
"""

from __future__ import annotations

from typing import Any

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
# Search verticals (/search, /news, /blog, /search/web, /cafe, /kin,
# /image, /video, /clip, /autocomplete)
# =============================================================================


class SearchResult(_BaseModel):
    """A single organic result on an integrated or web SERP."""

    position: int | None = None
    title: str | None = None
    url: str | None = None
    display_url: str | None = None
    snippet: str | None = None
    source: str | None = None


class RelatedSearch(_BaseModel):
    """A related-search suggestion attached to a SERP."""

    query: str | None = None
    url: str | None = None


class SearchResponse(_BaseModel):
    """Integrated (nexearch) SERP: organic results + inline Place pack."""

    query: str | None = None
    page: int | None = None
    result_count: int | None = None
    results: list[SearchResult] = Field(default_factory=list)
    related_searches: list[RelatedSearch] = Field(default_factory=list)
    place_results: list[dict[str, Any]] = Field(default_factory=list)
    url: str | None = None
    # view=more extended (ur.all) fields
    view: str | None = None
    start: int | None = None
    next_start: int | None = None
    has_more: bool | None = None


class NewsResult(_BaseModel):
    """A single news SERP result."""

    position: int | None = None
    title: str | None = None
    url: str | None = None
    snippet: str | None = None
    source: str | None = None
    published: str | None = None
    published_at: str | None = None
    thumbnail_url: str | None = None


class NewsResponse(_BaseModel):
    """News vertical SERP."""

    query: str | None = None
    page: int | None = None
    result_count: int | None = None
    results: list[NewsResult] = Field(default_factory=list)
    url: str | None = None


class BlogResult(_BaseModel):
    """A single blog SERP result."""

    position: int | None = None
    title: str | None = None
    url: str | None = None
    snippet: str | None = None
    blog_name: str | None = None
    author: str | None = None
    published: str | None = None
    published_at: str | None = None
    thumbnail_url: str | None = None


class BlogResponse(_BaseModel):
    """Blog vertical SERP."""

    query: str | None = None
    page: int | None = None
    result_count: int | None = None
    results: list[BlogResult] = Field(default_factory=list)
    url: str | None = None


class AutocompleteSuggestion(_BaseModel):
    """A single autocomplete suggestion."""

    query: str | None = None
    type: str | None = None


class AutocompleteResponse(_BaseModel):
    """Search-box autocomplete suggestions."""

    query: str | None = None
    suggestions: list[AutocompleteSuggestion] = Field(default_factory=list)
    result_count: int | None = None


class WebResult(_BaseModel):
    """A single web-vertical SERP result."""

    position: int | None = None
    title: str | None = None
    url: str | None = None
    display_url: str | None = None
    snippet: str | None = None


class WebSearchResponse(_BaseModel):
    """Web vertical SERP (15 docs/page)."""

    query: str | None = None
    page: int | None = None
    result_count: int | None = None
    results: list[WebResult] = Field(default_factory=list)
    url: str | None = None


class CafeResult(_BaseModel):
    """A single Cafe SERP result."""

    position: int | None = None
    title: str | None = None
    url: str | None = None
    cafe_name: str | None = None
    cafe_url: str | None = None
    snippet: str | None = None
    published: str | None = None
    published_at: str | None = None
    comment_count: int | None = None


class CafeResponse(_BaseModel):
    """Cafe vertical SERP (30/page)."""

    query: str | None = None
    page: int | None = None
    result_count: int | None = None
    results: list[CafeResult] = Field(default_factory=list)
    url: str | None = None


class KinResult(_BaseModel):
    """A single Knowledge iN SERP result."""

    position: int | None = None
    title: str | None = None
    url: str | None = None
    question: str | None = None
    answer: str | None = None
    author: str | None = None
    published: str | None = None
    published_at: str | None = None


class KinResponse(_BaseModel):
    """Knowledge iN vertical SERP (10/page)."""

    query: str | None = None
    page: int | None = None
    result_count: int | None = None
    results: list[KinResult] = Field(default_factory=list)
    url: str | None = None


class ImageResult(_BaseModel):
    """A single image SERP result."""

    position: int | None = None
    img_id: str | None = None
    title: str | None = None
    url: str | None = None
    source: str | None = None
    thumbnail_url: str | None = None
    original_url: str | None = None
    width: int | None = None
    height: int | None = None
    published: str | None = None
    published_at: str | None = None


class ImageResponse(_BaseModel):
    """Image vertical SERP (JSON API 100/page)."""

    query: str | None = None
    page: int | None = None
    result_count: int | None = None
    results: list[ImageResult] = Field(default_factory=list)
    url: str | None = None


class VideoResult(_BaseModel):
    """A single video SERP result."""

    position: int | None = None
    title: str | None = None
    url: str | None = None
    duration: str | None = None
    channel: str | None = None
    channel_url: str | None = None
    channel_thumbnail_url: str | None = None
    source: str | None = None
    published: str | None = None
    published_at: str | None = None
    view_count: int | None = None
    thumbnail_url: str | None = None


class VideoResponse(_BaseModel):
    """Video vertical SERP with /more pagination (step 48)."""

    query: str | None = None
    page: int | None = None
    result_count: int | None = None
    results: list[VideoResult] = Field(default_factory=list)
    url: str | None = None


class ClipResult(_BaseModel):
    """A single clip SERP result."""

    position: int | None = None
    title: str | None = None
    url: str | None = None
    author: str | None = None
    published: str | None = None
    published_at: str | None = None
    view_count: int | None = None


class ClipResponse(_BaseModel):
    """Clip vertical SERP with /more pagination (step 24)."""

    query: str | None = None
    page: int | None = None
    result_count: int | None = None
    results: list[ClipResult] = Field(default_factory=list)
    url: str | None = None


# =============================================================================
# Local + Place (/local, /place/{place_id}, .../reviews, .../photos)
# =============================================================================


class PlaceSummary(_BaseModel):
    """A place card as returned by /local and inline Place packs."""

    place_id: str | None = None
    name: str | None = None
    category: str | None = None
    address: str | None = None
    road_address: str | None = None
    phone: str | None = None
    rating: float | None = None
    review_count: int | None = None
    is_open: bool | None = None
    open_status_text: str | None = None
    description: str | None = None
    coupon_text: str | None = None
    badges: list[str] = Field(default_factory=list)
    thumbnail_url: str | None = None
    url: str | None = None
    rank: int | None = None


class LocalSearchResponse(_BaseModel):
    """Local business search (map pack)."""

    query: str | None = None
    result_count: int | None = None
    total_results: int | None = None
    results: list[PlaceSummary] = Field(default_factory=list)
    url: str | None = None


class MenuEntry(_BaseModel):
    """A single menu item on a place detail."""

    name: str | None = None
    price: str | None = None
    description: str | None = None
    image_url: str | None = None


class PlaceDetailResponse(_BaseModel):
    """Full place detail (business profile)."""

    place_id: str | None = None
    name: str | None = None
    category: str | None = None
    categories: list[str] = Field(default_factory=list)
    address: str | None = None
    road_address: str | None = None
    phone: str | None = None
    website: str | None = None
    rating: float | None = None
    review_count: int | None = None
    is_open: bool | None = None
    open_status_text: str | None = None
    description: str | None = None
    menus: list[MenuEntry] = Field(default_factory=list)
    images: list[str] = Field(default_factory=list)
    latitude: float | None = None
    longitude: float | None = None
    url: str | None = None
    source_url: str | None = None
    hours: list[dict[str, Any]] = Field(default_factory=list)
    payment_info: list[Any] = Field(default_factory=list)
    conveniences: list[Any] = Field(default_factory=list)
    top_photos: list[Any] = Field(default_factory=list)


class PlaceReview(_BaseModel):
    """A single place review."""

    review_id: str | None = None
    rating: float | None = None
    body: str | None = None
    author: str | None = None
    author_id: str | None = None
    visit_count: int | None = None
    view_count: int | None = None
    origin_type: str | None = None
    visited: str | None = None
    visited_at: str | None = None
    created: str | None = None
    voted_keywords: list[Any] = Field(default_factory=list)
    images: list[str] = Field(default_factory=list)
    has_reply: bool | None = None


class PlaceReviewsResponse(_BaseModel):
    """Paginated place reviews."""

    place_id: str | None = None
    review_count: int | None = None
    rating: float | None = None
    result_count: int | None = None
    source_url: str | None = None
    reviews: list[PlaceReview] = Field(default_factory=list)
    next_cursor: str | None = None
    total: int | None = None


class PlacePhoto(_BaseModel):
    """A single place photo / video."""

    photo_id: str | None = None
    original_url: str | None = None
    thumbnail_url: str | None = None
    width: int | None = None
    height: int | None = None
    title: str | None = None
    date_text: str | None = None
    media_format: str | None = None
    media_source: str | None = None
    rating: int | None = None


class PlacePhotosResponse(_BaseModel):
    """Paginated place photos."""

    place_id: str | None = None
    media_source: str | None = None
    result_count: int | None = None
    photos: list[PlacePhoto] = Field(default_factory=list)
    next_cursor: str | None = None
    has_next: bool | None = None


# =============================================================================
# Shopping — rankings, insight, categories (/shopping/*)
# =============================================================================


class ShoppingBestsellerProduct(_BaseModel):
    """A single product on a shopping bestseller list."""

    rank: int | None = None
    nv_mid: str | None = None
    product_id: str | None = None
    channel_product_id: str | None = None
    title: str | None = None
    price: int | None = None
    discount_price: int | None = None
    discount_rate: int | None = None
    review_score: float | None = None
    review_count: int | None = None
    mall_name: str | None = None
    mall_url: str | None = None
    image_url: str | None = None
    product_url: str | None = None
    delivery_fee: int | None = None
    is_ad: bool | None = None


class ShoppingBestsellersResponse(_BaseModel):
    """Shopping bestseller ranking."""

    category_id: str | None = None
    age_type: str | None = None
    sort_type: str | None = None
    period_type: str | None = None
    sync_date: str | None = None
    result_count: int | None = None
    products: list[ShoppingBestsellerProduct] = Field(default_factory=list)


class ShoppingKeyword(_BaseModel):
    """A single ranked shopping keyword."""

    rank: int | None = None
    keyword: str | None = None
    sub_title: str | None = None
    tags: list[str] = Field(default_factory=list)
    status: str | None = None
    rank_fluctuation: int | None = None
    category_id: str | None = None
    category_path: list[str] = Field(default_factory=list)


class ShoppingKeywordRankResponse(_BaseModel):
    """Shopping keyword ranking."""

    category_id: str | None = None
    age_type: str | None = None
    sort_type: str | None = None
    period_type: str | None = None
    result_count: int | None = None
    keywords: list[ShoppingKeyword] = Field(default_factory=list)


class InsightKeyword(_BaseModel):
    """A single keyword on a shopping insight list."""

    rank: int | None = None
    keyword: str | None = None


class ShoppingInsightResponse(_BaseModel):
    """Shopping insight top keywords for a category and date range."""

    category_id: str | None = None
    date_range: str | None = None
    result_count: int | None = None
    keywords: list[InsightKeyword] = Field(default_factory=list)


class ShoppingCategory(_BaseModel):
    """A single top-level shopping category."""

    category_id: str | None = None
    name: str | None = None


class ShoppingCategoriesResponse(_BaseModel):
    """Top-level shopping categories."""

    result_count: int | None = None
    categories: list[ShoppingCategory] = Field(default_factory=list)


class ShoppingSearchProductsResponse(_BaseModel):
    """Finder shopping search product cards (preview)."""

    query: str | None = None
    tab: str | None = None
    preview_only: bool | None = None
    result_count: int | None = None
    total_pages: int | None = None
    products: list[dict[str, Any]] = Field(default_factory=list)


class FilterValue(_BaseModel):
    """A single selectable value on a shopping search filter."""

    id: str | None = None
    name: str | None = None


class ShoppingFilter(_BaseModel):
    """A single shopping search filter facet."""

    id: str | None = None
    name: str | None = None
    filter_name: str | None = None
    type: str | None = None
    source_type: str | None = None
    values: list[FilterValue] = Field(default_factory=list)


class ShoppingSearchFiltersResponse(_BaseModel):
    """Available filters (brands/attributes) for a shopping search query."""

    query: str | None = None
    result_count: int | None = None
    filters: list[ShoppingFilter] = Field(default_factory=list)
    category_id: str | None = None


class ShoppingDealsResponse(_BaseModel):
    """snxbest gendered deal products."""

    gender: str | None = None
    result_count: int | None = None
    products: list[dict[str, Any]] = Field(default_factory=list)


class ShoppingVerticalResponse(_BaseModel):
    """snxbest vertical products (fashiontown / shoppinglive / logistics)."""

    vertical: str | None = None
    result_count: int | None = None
    products: list[dict[str, Any]] = Field(default_factory=list)


class ShoppingItItemsResponse(_BaseModel):
    """snxbest "IT items" curated cards."""

    result_count: int | None = None
    cards: list[dict[str, Any]] = Field(default_factory=list)
    best_cards: list[dict[str, Any]] = Field(default_factory=list)


class ShoppingCategoryTreeResponse(_BaseModel):
    """Shopping category tree (one level)."""

    parent_id: str | None = None
    level: str | None = None
    result_count: int | None = None
    categories: list[dict[str, Any]] = Field(default_factory=list)


class ShoppingFilteredProductsResponse(_BaseModel):
    """Filtered finder shopping products (brand/attribute)."""

    query: str | None = None
    brand_ids: list[str] = Field(default_factory=list)
    attribute_ids: list[str] = Field(default_factory=list)
    preview_only: bool | None = None
    result_count: int | None = None
    page_count: int | None = None
    page_size: int | None = None
    total_count: int | None = None
    filters_applied_by: str | None = None
    products: list[dict[str, Any]] = Field(default_factory=list)


class ShoppingBrandRankEntry(_BaseModel):
    """A single ranked brand on the snxbest brand ranking."""

    rank: int | None = None
    rank_id: str | None = None
    title: str | None = None
    status: str | None = None
    chart_type: str | None = None
    tags: list[str] = Field(default_factory=list)
    brand_seq: str | None = None
    brand_channel_seq: str | None = None
    brand_name: str | None = None
    brand_logo_url: str | None = None
    brand_url: str | None = None
    sync_date: str | None = None
    synced_at: str | None = None


class ShoppingBrandRankResponse(_BaseModel):
    """snxbest brand ranking (top 20 fixed list)."""

    category_id: str | None = None
    age_type: str | None = None
    sort_type: str | None = None
    period_type: str | None = None
    result_count: int | None = None
    brands: list[ShoppingBrandRankEntry] = Field(default_factory=list)


class ShoppingBrandCategoriesResponse(_BaseModel):
    """snxbest brand-ranking category tree (DIV1, or DIV2 children)."""

    depth: str | None = None
    parent_id: str | None = None
    result_count: int | None = None
    categories: list[dict[str, Any]] = Field(default_factory=list)


class KeywordPeriod(_BaseModel):
    """A single available keyword-rank period."""

    ymd: str | None = None
    ended_at: str | None = None
    month: int | None = None
    week: int | None = None
    period_type: str | None = None
    has_next: bool | None = None
    has_prev: bool | None = None


class ShoppingKeywordPeriodsResponse(_BaseModel):
    """Available snxbest keyword-rank periods."""

    category_id: str | None = None
    age_type: str | None = None
    sort_type: str | None = None
    period_type: str | None = None
    result_count: int | None = None
    periods: list[KeywordPeriod] = Field(default_factory=list)


class ShoppingCatalogSearchResponse(_BaseModel):
    """Full-catalog shopping search (SSR page 1 + paged XHR pages 2-5)."""

    query: str | None = None
    sort: str | None = None
    page: int | None = None
    page_size: int | None = None
    total: int | None = None
    cursor: int | None = None
    has_more: bool | None = None
    result_count: int | None = None
    preview_only: bool | None = None
    products: list[dict[str, Any]] = Field(default_factory=list)
    pages: list[dict[str, Any]] = Field(default_factory=list)
    source_url: str | None = None


class PriceCompareOffer(_BaseModel):
    """A single seller offer on a price-comparison catalog product."""

    mall_name: str | None = None
    price: int | None = None
    nv_mid: str | None = None
    product_id: str | None = None
    mall_seq: str | None = None
    naver_pay: bool | None = None


class PriceCompareEntry(_BaseModel):
    """A single catalog product with its seller offers."""

    catalog_id: str | None = None
    catalog_name: str | None = None
    offer_count: int | None = None
    best_price: int | None = None
    offers: list[PriceCompareOffer] = Field(default_factory=list)
    price_by_mall: str | None = None


class PriceCompareResponse(_BaseModel):
    """Seller offers per catalog product (가격비교)."""

    query: str | None = None
    entries: list[PriceCompareEntry] = Field(default_factory=list)
    offers: list[PriceCompareOffer] = Field(default_factory=list)
    offers_note: str | None = None


# =============================================================================
# Stores (/stores/{store_url}/*)
# =============================================================================


class StoreProfileResponse(_BaseModel):
    """SmartStore / Brand store profile."""

    store_url: str | None = None
    host: str | None = None
    channel_uid: str | None = None
    channel_no: str | None = None
    channel_name: str | None = None
    description: str | None = None
    logo_url: str | None = None
    sns: dict[str, Any] | None = None
    follower_count: int | None = None
    seller_grade: str | None = None
    sale_count: int | None = None
    cs_response_ratio: float | None = None
    business_type: str | None = None
    represent_type: str | None = None
    channel_service_type: str | None = None


class StoreCategory(_BaseModel):
    """A single store category."""

    category_id: str | None = None
    parent_category_id: str | None = None
    name: str | None = None
    level: int | None = None
    sort_order: int | None = None
    all_product_category: bool | None = None
    exposure: bool | None = None
    type: str | None = None


class StoreCategoriesResponse(_BaseModel):
    """Store category list."""

    store_url: str | None = None
    host: str | None = None
    result_count: int | None = None
    categories: list[StoreCategory] = Field(default_factory=list)


class StoreProductsResponse(_BaseModel):
    """Store product listing (listing card union)."""

    store_url: str | None = None
    host: str | None = None
    total_count: int | None = None
    page: int | None = None
    page_size: int | None = None
    sort: str | None = None
    products: list[dict[str, Any]] = Field(default_factory=list)


class StoreBestsellersResponse(_BaseModel):
    """Store bestseller list (listing card union)."""

    store_url: str | None = None
    host: str | None = None
    period: str | None = None
    result_count: int | None = None
    products: list[dict[str, Any]] = Field(default_factory=list)


# =============================================================================
# Products + reviews + Q&A (/products/*, /reviews/*, /product-groups/*)
# =============================================================================


class ReviewDetailResponse(_BaseModel):
    """Commerce review detail by id (batch of requested ids)."""

    requested_ids: list[str] = Field(default_factory=list)
    reviews: list[dict[str, Any]] = Field(default_factory=list)
    missing_ids: list[str] = Field(default_factory=list)


class ProductReviewSummaryResponse(_BaseModel):
    """Product rating summary."""

    origin_product_no: str | None = None
    leaf_category_id: str | None = None
    review_count: int | None = None
    average_review_score: float | None = None


class PaginatedReviewsResponse(_BaseModel):
    """Paginated product review list."""

    origin_product_no: str | None = None
    page: int | None = None
    page_size: int | None = None
    sort: str | None = None
    total_count: int | None = None
    reviews: list[dict[str, Any]] = Field(default_factory=list)


class ProductQna(_BaseModel):
    """A single product Q&A entry."""

    question: str | None = None
    answer: str | None = None
    author_masked: str | None = None
    created_at: str | None = None
    answered_at: str | None = None


class ProductQnaResponse(_BaseModel):
    """Paginated product Q&A list."""

    origin_product_no: str | None = None
    page: int | None = None
    total_count: int | None = None
    qnas: list[ProductQna] = Field(default_factory=list)


class ProductDetailResponse(_BaseModel):
    """Full product detail (PDP)."""

    product_no: str | None = None
    name: str | None = None
    price: int | None = None
    discount_price: int | None = None
    discount_rate: int | None = None
    rating: float | None = None
    review_count: int | None = None
    brand: str | None = None
    manufacturer: str | None = None
    images: list[str] = Field(default_factory=list)
    options: list[dict[str, Any]] = Field(default_factory=list)
    delivery: dict[str, Any] | None = None
    seller: dict[str, Any] | None = None
    category: dict[str, Any] | None = None
    reg_date: str | None = None
    registered_at: str | None = None
    mod_date: str | None = None
    modified_at: str | None = None
    detail_source: str | None = None
    missing_fields: list[str] = Field(default_factory=list)


class ReviewVideoInkeyResponse(_BaseModel):
    """Video playback key minted from attachVid + videoStamp."""

    video_id: str | None = None
    in_key: str | None = None


class ReviewSsrQueriesResponse(_BaseModel):
    """SSR page query recipes for a review."""

    review_id: str | None = None
    source_url: str | None = None
    queries: dict[str, Any] | None = None


class GroupProductGraphResponse(_BaseModel):
    """Storefront variant-group graph."""

    origin_product_no: str | None = None
    group_id: str | None = None
    origin_product_nos: list[str] = Field(default_factory=list)
    is_grouped: bool | None = None


class GroupReviewSummaryResponse(_BaseModel):
    """Group-level rating summary (same shape as product review-summary)."""

    group_product_no: str | None = None
    leaf_category_id: str | None = None
    review_count: int | None = None
    average_review_score: float | None = None


# =============================================================================
# Shopping Live (/shopping/live/*)
# =============================================================================


class LiveSearchKeywordsResponse(_BaseModel):
    """Shopping Live search standby keyword ranking."""

    keyword_ranking: dict[str, Any] | None = None
    recent_keywords: list[Any] = Field(default_factory=list)
    result_count: int | None = None
    source_url: str | None = None


class LiveBroadcastDetailResponse(_BaseModel):
    """Broadcast detail including embedded shoppingProducts."""

    broadcast_id: str | None = None
    item_count: int | None = None
    source_url: str | None = None
    broadcast: dict[str, Any] | None = None


class LiveBroadcastProductsResponse(_BaseModel):
    """Paginated product list for one broadcast."""

    broadcast_id: str | None = None
    page: int | None = None
    total_count: int | None = None
    total_page: int | None = None
    result_count: int | None = None
    products: list[dict[str, Any]] = Field(default_factory=list)


class LiveBroadcastCountsResponse(_BaseModel):
    """Broadcast viewer/like/comment counts."""

    broadcast_id: str | None = None
    counts: dict[str, Any] | None = None


class LiveChannelProfileResponse(_BaseModel):
    """Shopping Live channel / store profile."""

    channel_id: str | None = None
    profile: dict[str, Any] | None = None


class LiveChannelProductsResponse(_BaseModel):
    """Channel product list."""

    channel_id: str | None = None
    count: int | None = None
    next: str | None = None
    result_count: int | None = None
    products: list[dict[str, Any]] = Field(default_factory=list)


class LiveChannelBroadcastsResponse(_BaseModel):
    """Channel broadcast list including upcoming STANDBY schedule cards."""

    channel_id: str | None = None
    count: int | None = None
    next: str | None = None
    result_count: int | None = None
    broadcasts: list[dict[str, Any]] = Field(default_factory=list)


class LiveChannelShortclipsResponse(_BaseModel):
    """Channel shorts/clips list."""

    channel_id: str | None = None
    count: int | None = None
    next: str | None = None
    result_count: int | None = None
    shortclips: list[dict[str, Any]] = Field(default_factory=list)


class LiveShortclipDetailResponse(_BaseModel):
    """Shortclip detail with embedded products and categories."""

    shortclip_id: str | None = None
    item_count: int | None = None
    shortclip: dict[str, Any] | None = None


class LiveShortclipProductsResponse(_BaseModel):
    """Paginated shortclip product list."""

    shortclip_id: str | None = None
    page: int | None = None
    total_count: int | None = None
    total_page: int | None = None
    result_count: int | None = None
    products: list[dict[str, Any]] = Field(default_factory=list)


class LiveReplayProductsResponse(_BaseModel):
    """Replay product timeline of an ended broadcast."""

    broadcast_id: str | None = None
    next: str | None = None
    result_count: int | None = None
    product_count: int | None = None
    entries: list[dict[str, Any]] = Field(default_factory=list)


class LiveProductCategory(_BaseModel):
    """A single product category present in a broadcast."""

    id: str | None = None
    name: str | None = None


class LiveBroadcastCategoriesResponse(_BaseModel):
    """Product categories present in a broadcast."""

    broadcast_id: str | None = None
    result_count: int | None = None
    categories: list[LiveProductCategory] = Field(default_factory=list)
