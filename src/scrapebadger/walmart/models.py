"""Pydantic models for Walmart API responses.

These models mirror the backend ``walmart_scraper`` response schema
field-for-field. All models are immutable (frozen) and ignore unknown fields
for forward compatibility.

Field coverage is deliberately a SUPERSET of what the competing providers
return: UPC, per-fulfilment SLA and delivery dates, return policy, condition
offers, marketplace seller ratings, AI review summaries, review aspect
breakdowns, nutrition/warnings/warranty, store services and hours.

Walmart is US-only — walmart.com is the single supported market, so no model
carries a market/country selector.
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
# Shared value objects
# =============================================================================


class Price(_BaseModel):
    """A single price point. Walmart nests several of these per item."""

    price: float | None = None
    currency: str | None = None
    price_string: str | None = None
    price_display: str | None = None
    support_text: str | None = None
    variant_price_string: str | None = None


class PriceRange(_BaseModel):
    """Min/max price span for a multi-variant or gift-card item."""

    min_price: float | None = None
    max_price: float | None = None
    currency: str | None = None
    price_string: str | None = None
    denominations: list[float] = Field(default_factory=list)


class PriceInfo(_BaseModel):
    """The full price block — current, was/list, unit, savings and range."""

    current_price: Price | None = None
    was_price: Price | None = None
    list_price: Price | None = None
    unit_price: Price | None = None
    comparison_price: Price | None = None
    subscription_price: Price | None = None
    shipping_price: Price | None = None
    price_range: PriceRange | None = None
    savings_amount: float | None = None
    savings_string: str | None = None
    is_price_reduced: bool | None = None
    price_display_codes: dict[str, Any] = Field(default_factory=dict)
    additional_fees: list[dict[str, Any]] = Field(default_factory=list)
    volume_price_tiers: list[dict[str, Any]] = Field(default_factory=list)


class Image(_BaseModel):
    """A product image."""

    id: str | None = None
    url: str | None = None
    zoomable: bool | None = None


class Video(_BaseModel):
    """A product video with its renditions and captions."""

    title: str | None = None
    poster: str | None = None
    versions: dict[str, Any] = Field(default_factory=dict)
    captions: list[dict[str, Any]] = Field(default_factory=list)


class Breadcrumb(_BaseModel):
    """One taxonomy hop."""

    name: str | None = None
    url: str | None = None


class NameValue(_BaseModel):
    """Specification / highlight / warning / at-a-glance row."""

    name: str | None = None
    value: str | None = None
    icon_url: str | None = None


class SpecificationGroup(_BaseModel):
    """A named group of specification rows."""

    group_name: str | None = None
    specifications: list[NameValue] = Field(default_factory=list)


class Badge(_BaseModel):
    """A merchandising badge (rollback, best seller, …)."""

    id: str | None = None
    text: str | None = None
    type: str | None = None
    key: str | None = None


class FulfillmentOption(_BaseModel):
    """Shipping / pickup / delivery option with its live availability."""

    type: str | None = None
    availability_status: str | None = None
    availability_type: str | None = None
    inventory_status: str | None = None
    available_quantity: int | None = None
    is_low_in_stock: bool | None = None
    location_text: str | None = None
    max_order_quantity: int | None = None
    order_limit: int | None = None
    restricted: bool | None = None
    selected: bool | None = None
    speed_details: dict[str, Any] | None = None


class FulfillmentSummary(_BaseModel):
    """Per-method SLA and promised delivery dates."""

    fulfillment: str | None = None
    fulfillment_badge: str | None = None
    fulfillment_price: float | None = None
    fulfillment_methods: list[str] = Field(default_factory=list)
    delivery_date: str | None = None
    max_delivery_date: str | None = None
    store_delivery_date: str | None = None
    store_max_delivery_date: str | None = None
    store_id: str | None = None
    store_timezone: str | None = None
    #: Walmart returns SLA as a structured object
    #: (``{unitOfMeasure, minimumValue, maximumValue, rank}``), not a string.
    sla: dict[str, Any] | None = None
    regular_sla: dict[str, Any] | None = None
    calculated_sla_days: int | None = None
    is_express: bool | None = None
    is_free_for_wplus: bool | None = None


class ReturnPolicy(_BaseModel):
    """Returnability window and conditions."""

    returnable: bool | None = None
    returnable_to_store: bool | None = None
    free_returns: bool | None = None
    return_window: str | None = None
    return_policy_type: str | None = None
    return_policy_text: str | None = None
    return_policy_condition: str | None = None
    return_location: str | None = None
    holiday_return_enabled: bool | None = None


class Variant(_BaseModel):
    """One selectable variant (colour / size / capacity …)."""

    id: str | None = None
    us_item_id: str | None = None
    name: str | None = None
    variant_type: str | None = None
    value: str | None = None
    type_name: str | None = None
    value_name: str | None = None
    url: str | None = None
    price: float | None = None
    in_stock: bool | None = None
    available: bool | None = None
    selected: bool | None = None
    image_url: str | None = None
    images: list[str] = Field(default_factory=list)
    swatch_image_url: str | None = None


class ConditionOffer(_BaseModel):
    """Refurbished / pre-owned / new alternative offer on the same product."""

    offer_id: str | None = None
    condition: str | None = None
    is_condition_new: bool | None = None
    availability_status: str | None = None
    price: float | None = None
    price_string: str | None = None
    #: Walmart returns this as null, a bool, or a nested object depending on the
    #: item — normalised to "are there other conditions on offer?".
    more_conditions: bool | None = None


class Promotion(_BaseModel):
    """A promotion or offer attached to the product."""

    id: str | None = None
    type: str | None = None
    description: str | None = None
    terms: str | None = None


class NutritionFacts(_BaseModel):
    """Grocery items only — Walmart's structured nutrition block."""

    calorie_info: dict[str, Any] | None = None
    key_nutrients: dict[str, Any] | None = None
    vitamin_minerals: dict[str, Any] | None = None
    serving_info: dict[str, Any] | None = None
    additional_disclaimer: str | None = None


class Warranty(_BaseModel):
    """Manufacturer warranty text and link."""

    information: str | None = None
    length: str | None = None
    url: str | None = None


class LocationContext(_BaseModel):
    """Which store/postcode Walmart resolved this response against.

    Walmart derives the assortment store from the exit IP's geography — it
    cannot be pinned by cookie or query param. Prices and availability are
    therefore store-specific whether the caller asked for it or not, so the
    resolved location is returned explicitly rather than left implicit.
    """

    postal_code: str | None = None
    city: str | None = None
    state: str | None = None
    store_id: str | None = None
    intent: str | None = None


class EmbeddedSeller(_BaseModel):
    """Seller as it appears on a product — not the full seller profile."""

    seller_id: str | None = None
    catalog_seller_id: str | None = None
    seller_name: str | None = None
    seller_display_name: str | None = None
    seller_type: str | None = None
    seller_logo_url: str | None = None
    seller_storefront_url: str | None = None
    seller_average_rating: float | None = None
    seller_review_count: int | None = None
    has_seller_badge: bool | None = None
    is_pro_seller: bool | None = None
    wfs_enabled: bool | None = None
    wfs_provider_name: str | None = None


# =============================================================================
# Reviews
# =============================================================================


class RatingDistribution(_BaseModel):
    """The full star histogram plus its percentage form."""

    average_rating: float | None = None
    rounded_average_rating: float | None = None
    total_review_count: int | None = None
    reviews_with_text_count: int | None = None
    recommended_percentage: int | None = None
    total_media_count: int | None = None
    one_star: int | None = None
    two_star: int | None = None
    three_star: int | None = None
    four_star: int | None = None
    five_star: int | None = None
    one_star_percent: int | None = None
    two_star_percent: int | None = None
    three_star_percent: int | None = None
    four_star_percent: int | None = None
    five_star_percent: int | None = None


class Review(_BaseModel):
    """A single customer review."""

    review_id: str | None = None
    rating: int | None = None
    title: str | None = None
    text: str | None = None
    author: str | None = None
    submitted_at: str | None = None
    submitted_utc: float | None = None
    verified_purchase: bool | None = None
    helpful_count: int | None = None
    not_helpful_count: int | None = None
    photos: list[str] = Field(default_factory=list)
    media: list[dict[str, Any]] = Field(default_factory=list)
    badges: list[Badge] = Field(default_factory=list)
    user_badges: list[Badge] = Field(default_factory=list)
    seller_name: str | None = None
    fulfilled_by: str | None = None
    condition: str | None = None
    syndication_source: str | None = None
    original_language: str | None = None
    aspects: list[dict[str, Any]] = Field(default_factory=list)
    client_responses: list[dict[str, Any]] = Field(default_factory=list)


# =============================================================================
# Product
# =============================================================================


class Product(_BaseModel):
    """Full Walmart product detail (PDP)."""

    # Identity
    us_item_id: str | None = None
    item_id: str | None = None
    product_id: str | None = None
    primary_product_id: str | None = None
    offer_id: str | None = None
    upc: str | None = None
    gtin: str | None = None
    model: str | None = None
    manufacturer_product_id: str | None = None
    sku: str | None = None

    # Descriptive
    name: str | None = None
    brand: str | None = None
    brand_url: str | None = None
    short_description: str | None = None
    long_description: str | None = None
    #: Walmart's own generative-AI product content. ``ai_description_html`` is an
    #: HTML ``<ul>``; ``ai_highlights`` is a structured highlight list.
    ai_description_html: str | None = None
    ai_highlights: list[NameValue] = Field(default_factory=list)
    url: str | None = None
    canonical_url: str | None = None
    item_type: str | None = None
    product_type_id: str | None = None
    class_type: str | None = None
    sales_unit: str | None = None
    gender: str | None = None

    # Taxonomy
    category_path: str | None = None
    category_path_id: str | None = None
    breadcrumbs: list[Breadcrumb] = Field(default_factory=list)
    department_name: str | None = None

    # Media
    image_url: str | None = None
    images: list[Image] = Field(default_factory=list)
    videos: list[Video] = Field(default_factory=list)

    # Pricing
    price: float | None = None
    currency: str | None = None
    price_info: PriceInfo | None = None
    promotions: list[Promotion] = Field(default_factory=list)
    promo_text: str | None = None

    # Availability & fulfilment
    availability_status: str | None = None
    in_stock: bool | None = None
    is_out_of_stock: bool | None = None
    fulfillment_type: str | None = None
    fulfillment_options: list[FulfillmentOption] = Field(default_factory=list)
    fulfillment_summary: list[FulfillmentSummary] = Field(default_factory=list)
    shipping_option: str | None = None
    pickup_option: str | None = None
    order_limit: int | None = None
    order_min_limit: int | None = None
    is_preorder: bool | None = None
    is_blitz_item: bool | None = None
    aisle: str | None = None
    location: LocationContext | None = None
    add_on_services: list[dict[str, Any]] = Field(default_factory=list)
    has_care_plans: bool | None = None

    # Ratings
    rating: float | None = None
    review_count: int | None = None

    # Seller
    seller: EmbeddedSeller | None = None
    additional_offer_count: int | None = None
    transactable_offer_count: int | None = None
    condition_offers: list[ConditionOffer] = Field(default_factory=list)

    # Condition
    condition: str | None = None
    is_condition_new: bool | None = None
    is_preowned: bool | None = None
    preowned_condition: str | None = None

    # Variants
    variants: list[Variant] = Field(default_factory=list)
    variant_criteria: list[dict[str, Any]] = Field(default_factory=list)
    selected_variant_ids: list[str] = Field(default_factory=list)

    # Rich content
    specifications: list[NameValue] = Field(default_factory=list)
    specification_groups: list[SpecificationGroup] = Field(default_factory=list)
    highlights: list[NameValue] = Field(default_factory=list)
    warnings: list[NameValue] = Field(default_factory=list)
    warranty: Warranty | None = None
    nutrition_facts: NutritionFacts | None = None
    ingredients: str | None = None
    badges: list[Badge] = Field(default_factory=list)
    trust_badges: list[dict[str, Any]] = Field(default_factory=list)
    return_policy: ReturnPolicy | None = None
    product_disclaimers: list[dict[str, Any]] = Field(default_factory=list)

    # Eligibility flags buyers actually filter on
    snap_eligible: bool | None = None
    fsa_eligible: bool | None = None
    subscription_eligible: bool | None = None
    is_customizable: bool | None = None
    free_shipping: bool | None = None
    buy_now_eligible: bool | None = None
    legal_restriction: str | None = None

    # Reviews sample (saves a second call for shallow use cases)
    rating_distribution: RatingDistribution | None = None
    top_reviews: list[Review] = Field(default_factory=list)
    review_aspects: list[dict[str, Any]] = Field(default_factory=list)
    review_summary: str | None = None


# =============================================================================
# Search / category
# =============================================================================


class SearchItem(_BaseModel):
    """One product card in a search or category result set."""

    us_item_id: str | None = None
    item_id: str | None = None
    product_id: str | None = None
    offer_id: str | None = None
    name: str | None = None
    brand: str | None = None
    manufacturer_name: str | None = None
    url: str | None = None
    canonical_url: str | None = None
    image_url: str | None = None
    images: list[str] = Field(default_factory=list)
    description: str | None = None
    short_description: str | None = None

    price: float | None = None
    currency: str | None = None
    price_string: str | None = None
    was_price: float | None = None
    price_info: PriceInfo | None = None
    price_per_unit: str | None = None

    rating: float | None = None
    review_count: int | None = None

    in_stock: bool | None = None
    is_out_of_stock: bool | None = None
    availability_status: str | None = None
    fulfillment_type: str | None = None
    fulfillment_badges: list[str] = Field(default_factory=list)
    fulfillment_speed: list[str] = Field(default_factory=list)
    shipping_option: str | None = None

    seller_id: str | None = None
    seller_name: str | None = None
    seller_type: str | None = None

    is_sponsored: bool | None = None
    is_two_day_shipping: bool | None = None
    badges: list[Badge] = Field(default_factory=list)
    variants: list[Variant] = Field(default_factory=list)
    category: str | None = None
    department_name: str | None = None
    item_type: str | None = None
    condition: str | None = None
    is_preowned: bool | None = None
    snap_eligible: bool | None = None
    position: int | None = None
    stack_position: int | None = None
    product_location: str | None = None
    additional_offer_count: int | None = None


class SearchResponse(_BaseModel):
    """A page of search, category, deals or seller-catalogue results."""

    query: str | None = None
    url: str | None = None
    page: int = 1
    #: Walmart's OWN claimed total. Deliberately not called ``total_results``: it
    #: reports ~14,700 for a query that stops returning products after page 10.
    #: It moves correctly when a filter is applied, so it is a useful relative
    #: signal — just not a reachable count.
    total_results_reported: int | None = None
    #: The measured page ceiling for this surface (10 search / 11 browse).
    max_page: int | None = None
    result_count: int = 0
    has_more_pages: bool | None = None
    sort: str | None = None
    title: str | None = None
    breadcrumbs: list[Breadcrumb] = Field(default_factory=list)
    related_searches: list[str] = Field(default_factory=list)
    spelling_correction: str | None = None
    items: list[SearchItem] = Field(default_factory=list)


class ReviewsResponse(_BaseModel):
    """A page of customer reviews with the full star histogram."""

    item_id: str | None = None
    url: str | None = None
    page: int = 1
    sort: str | None = None
    result_count: int = 0
    distribution: RatingDistribution | None = None
    aspects: list[dict[str, Any]] = Field(default_factory=list)
    review_summary: str | None = None
    top_positive_review: Review | None = None
    top_negative_review: Review | None = None
    reviews: list[Review] = Field(default_factory=list)


# =============================================================================
# Seller
# =============================================================================


class Seller(_BaseModel):
    """A marketplace seller's public profile."""

    seller_id: str | None = None
    catalog_seller_id: str | None = None
    name: str | None = None
    display_name: str | None = None
    seller_type: str | None = None
    url: str | None = None
    logo_url: str | None = None
    banner_url: str | None = None
    about: str | None = None
    email: str | None = None
    phone: str | None = None
    address1: str | None = None
    address2: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country: str | None = None
    country_code: str | None = None
    rating: float | None = None
    review_count: int | None = None
    has_seller_badge: bool | None = None
    is_pro_seller: bool | None = None
    is_alcohol_seller: bool | None = None
    deactivation_status: str | None = None
    tax_policy: str | None = None


class SellerResponse(_BaseModel):
    """Seller profile.

    No product list: ``/seller/{id}`` renders its catalogue client-side. Use
    :meth:`~scrapebadger.walmart.sellers.SellersClient.get_seller_products` —
    it goes through search with a ``retailer_id`` facet, which does work.
    """

    seller: Seller
    featured_items: list[SearchItem] = Field(default_factory=list)


# =============================================================================
# Stores
# =============================================================================


class StoreHours(_BaseModel):
    """Opening hours for one day."""

    day: str | None = None
    start: str | None = None
    end: str | None = None
    closed: bool | None = None


class StoreService(_BaseModel):
    """An in-store department (pharmacy, deli, auto centre …).

    Each carries its OWN phone and opening hours, which differ from the store's.
    """

    name: str | None = None
    display_name: str | None = None
    phone: str | None = None
    open_24_hours: bool | None = None
    hours: list[StoreHours] = Field(default_factory=list)


class Store(_BaseModel):
    """A physical Walmart store."""

    store_id: str | None = None
    name: str | None = None
    display_name: str | None = None
    store_type: str | None = None
    phone: str | None = None
    address1: str | None = None
    address2: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    distance_miles: float | None = None
    timezone: str | None = None
    open_24_hours: bool | None = None
    is_spark_store: bool | None = None
    is_glass_eligible: bool | None = None
    hours: list[StoreHours] = Field(default_factory=list)
    services: list[StoreService] = Field(default_factory=list)
    access_types: list[str] = Field(default_factory=list)


class StoreResponse(_BaseModel):
    """A store plus the stores around it — one fetch, several answers."""

    store: Store
    departments: list[str] = Field(default_factory=list)
    #: Populated only for stores with a fuel station.
    fuel_prices: list[dict[str, Any]] = Field(default_factory=list)
    nearby_count: int = 0
    nearby_stores: list[Store] = Field(default_factory=list)


# =============================================================================
# Autocomplete
# =============================================================================


class Suggestion(_BaseModel):
    """One search-box suggestion."""

    query: str | None = None
    type: str | None = None
    image_url: str | None = None
    url: str | None = None
    department_id: str | None = None
    department_name: str | None = None


class AutocompleteResponse(_BaseModel):
    """Search-box suggestions for a partial term."""

    query: str
    result_count: int = 0
    suggestions: list[Suggestion] = Field(default_factory=list)


# =============================================================================
# Reference
# =============================================================================


class Market(_BaseModel):
    """A supported Walmart market. Only ``US`` / walmart.com is supported."""

    code: str
    name: str
    domain: str
    currency: str
    language: str


class MarketsResponse(_BaseModel):
    """All supported Walmart markets."""

    result_count: int = 0
    markets: list[Market] = Field(default_factory=list)
