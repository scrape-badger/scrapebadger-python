"""Pydantic models for Wallapop API responses.

These models mirror the backend ``wallapop_scraper`` response schema
field-for-field. All models are immutable (frozen) and ignore unknown fields
for forward compatibility.

Wallapop is a second-hand marketplace for Spain, Italy and Portugal, selected
by ``market`` (es, it, pt). Every timestamp ships twice: ``*_utc`` (Unix
seconds, for maths/sorting) and ``*_at`` (ISO 8601 UTC, for people).
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
# Shared building blocks
# =============================================================================


class Image(_BaseModel):
    """One listing or profile image in three sizes."""

    id: str | None = None
    small: str | None = None
    medium: str | None = None
    large: str | None = None
    average_color: str | None = None


class Location(_BaseModel):
    """Where a listing or seller is (approximate when ``approximated``)."""

    latitude: float | None = None
    longitude: float | None = None
    postal_code: str | None = None
    city: str | None = None
    region: str | None = None
    region2: str | None = None
    country_code: str | None = None
    approximated: bool | None = None


class TaxonomyNode(_BaseModel):
    """One level of a listing's category path."""

    id: int
    name: str | None = None


class Attribute(_BaseModel):
    """One structured listing attribute, e.g. ``condition`` → good / "Buen estado"."""

    value: Any = None
    title: str | None = None
    text: str | None = None


# =============================================================================
# Search
# =============================================================================


class SearchItem(_BaseModel):
    """One listing in a search result page."""

    id: str
    user_id: str | None = None
    title: str | None = None
    description: str | None = None
    price: float | None = None
    currency: str | None = None
    category_id: int | None = None
    taxonomy: list[TaxonomyNode] = Field(default_factory=list)
    condition: str | None = None
    brand: str | None = None
    model: str | None = None
    attributes: dict[str, Any] = Field(
        default_factory=dict,
        description="Vertical-specific attributes (cars: year, km, gearbox, horsepower...)",
    )
    images: list[Image] = Field(default_factory=list)
    location: Location | None = None
    shippable: bool | None = None
    user_allows_shipping: bool | None = None
    reserved: bool | None = None
    bumped: bool = False
    bump_type: str | None = None
    is_top_profile: bool | None = None
    is_refurbished: bool | None = None
    has_warranty: bool | None = None
    slug: str | None = None
    url: str | None = None
    created_utc: float | None = None
    created_at: str | None = None
    modified_utc: float | None = None
    modified_at: str | None = None


class SearchResponse(_BaseModel):
    """One page of search results (40 per page, cursor pagination)."""

    items: list[SearchItem] = Field(default_factory=list)
    result_count: int = 0
    total_results: int | None = Field(
        default=None, description="Wallapop's own estimate of matching listings"
    )
    next_page: str | None = Field(default=None, description="Pass back as `next_page`")
    order_by: str | None = None
    market: str
    country_code: str | None = Field(default=None, description="Country Wallapop searched in")
    search_id: str | None = None


# =============================================================================
# Item detail
# =============================================================================


class ItemDetail(_BaseModel):
    """Full Wallapop listing detail."""

    id: str
    user_id: str | None = None
    title: str | None = None
    description: str | None = None
    vertical: str | None = Field(default=None, description="consumer_goods, cars, real_estate...")
    price: float | None = None
    currency: str | None = None
    category_id: int | None = None
    taxonomy: list[TaxonomyNode] = Field(default_factory=list)
    condition: str | None = None
    brand: str | None = None
    model: str | None = None
    attributes: dict[str, Attribute] = Field(default_factory=dict)
    characteristics: str | None = None
    characteristics_details: list[dict[str, str]] = Field(default_factory=list)
    hashtags: list[str] = Field(default_factory=list)
    images: list[Image] = Field(default_factory=list)
    location: Location | None = None
    shippable: bool | None = None
    user_allows_shipping: bool | None = None
    supports_shipping: bool | None = None
    bumped: bool = False
    bump_type: str | None = None
    is_top_profile: bool | None = None
    views: int | None = None
    favorites: int | None = None
    conversations: int | None = None
    slug: str | None = None
    url: str | None = None
    modified_utc: float | None = None
    modified_at: str | None = None


# =============================================================================
# Users
# =============================================================================


class UserValidations(_BaseModel):
    """Which verifications a Wallapop user has completed."""

    level: str | None = None
    email: bool | None = None
    mobile: bool | None = None
    facebook: bool | None = None
    google: bool | None = None
    picture: bool | None = None
    location: bool | None = None
    birthday: bool | None = None
    kyc: bool | None = None


class UserProfile(_BaseModel):
    """A Wallapop user's profile with ratings, sales counters and verifications."""

    id: str
    name: str | None = None
    type: str | None = Field(default=None, description="normal | professional")
    seller_type: str | None = Field(default=None, description="Private | Professional")
    verified: bool | None = None
    is_top_profile: bool | None = None
    featured: bool | None = None
    image: Image | None = None
    location: Location | None = None
    rating_average: float | None = Field(default=None, description="0-5")
    scoring_stars: float | None = Field(default=None, description="0-100")
    reviews_count: int | None = None
    published_count: int | None = None
    sold_count: int | None = None
    sells_count: int | None = None
    buys_count: int | None = None
    reports_received_count: int | None = None
    response_rate: str | None = None
    activity_level: str | None = None
    deliveries_on_time_in_days: int | None = None
    validations: UserValidations | None = None
    slug: str | None = None
    url: str | None = None
    registered_utc: float | None = None
    registered_at: str | None = None


class UserItem(_BaseModel):
    """One of a seller's live listings."""

    id: str
    title: str | None = None
    description: str | None = None
    price: float | None = None
    currency: str | None = None
    category_id: int | None = None
    condition: str | None = None
    attributes: dict[str, Any] = Field(default_factory=dict)
    images: list[Image] = Field(default_factory=list)
    shippable: bool | None = None
    user_allows_shipping: bool | None = None
    is_refurbished: bool | None = None
    has_warranty: bool | None = None
    slug: str | None = None
    url: str | None = None


class UserItemsResponse(_BaseModel):
    """One page of a seller's listings (40 per page, cursor pagination)."""

    user_id: str
    items: list[UserItem] = Field(default_factory=list)
    result_count: int = 0
    next_page: str | None = None
    market: str


class ReviewItem(_BaseModel):
    """The listing a review was left for."""

    id: str | None = None
    title: str | None = None
    category_id: int | None = None
    image: str | None = None
    slug: str | None = None
    url: str | None = None


class Reviewer(_BaseModel):
    """The user who left a review."""

    id: str | None = None
    name: str | None = None
    image: str | None = None
    slug: str | None = None


class Review(_BaseModel):
    """One review a Wallapop user received."""

    id: str | None = None
    rating: int | None = Field(default=None, description="1-5")
    scoring: int | None = Field(default=None, description="0-100")
    comment: str | None = None
    type: str | None = Field(
        default=None, description="sell = the profile sold to the reviewer; buy = bought from"
    )
    is_shipping_transaction: bool | None = None
    item: ReviewItem | None = None
    reviewer: Reviewer | None = None
    created_utc: float | None = None
    created_at: str | None = None


class ReviewsResponse(_BaseModel):
    """One page of a user's reviews (newest first, cursor pagination)."""

    user_id: str
    reviews: list[Review] = Field(default_factory=list)
    result_count: int = 0
    next_page: str | None = None
    market: str


# =============================================================================
# Reference: autocomplete, categories, filters, markets
# =============================================================================


class Suggestion(_BaseModel):
    """One search-box suggestion."""

    text: str
    subtitle: str | None = None
    type: str | None = Field(default=None, description="Upstream suggestion kind, e.g. regular")


class AutocompleteResponse(_BaseModel):
    query: str
    suggestions: list[Suggestion] = Field(default_factory=list)
    market: str


class Category(_BaseModel):
    """A category node; ``id`` is usable as the search ``category_id``."""

    id: int
    name: str | None = None
    parent_id: int | None = None
    vertical: str | None = None
    icon: str | None = None
    subcategories: list[Category] = Field(default_factory=list)


class CategoriesResponse(_BaseModel):
    categories: list[Category] = Field(default_factory=list)
    market: str


class FilterOption(_BaseModel):
    """One selectable value of a search filter."""

    id: str
    title: str | None = None


class SearchFilter(_BaseModel):
    """A search filter Wallapop offers for a category/query."""

    id: str
    title: str | None = None
    type: str | None = Field(default=None, description="list, toggle, slider, location, tree")
    params: list[str] = Field(
        default_factory=list, description="Wallapop search params this filter sets"
    )
    multi: bool | None = None
    options: list[FilterOption] = Field(default_factory=list)
    options_endpoint: bool = Field(
        default=False, description="Options are long — fetch them from filters/{id}/options"
    )


class FiltersResponse(_BaseModel):
    filters: list[SearchFilter] = Field(default_factory=list)
    market: str


class FilterOptionsResponse(_BaseModel):
    filter_id: str
    options: list[FilterOption] = Field(default_factory=list)
    market: str


class Market(_BaseModel):
    """A supported Wallapop market and its default search location."""

    code: str
    country_code: str
    name: str
    currency: str
    language: str
    default_latitude: float
    default_longitude: float


class MarketsResponse(_BaseModel):
    markets: list[Market] = Field(default_factory=list)
