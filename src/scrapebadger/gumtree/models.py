"""Pydantic models for Gumtree API responses.

These models mirror the backend ``gumtree_scraper`` response schema
field-for-field. All models are immutable (frozen) and ignore unknown fields
for forward compatibility.

Gumtree is UK-only — gumtree.com is the single supported market. Prices are
in GBP. Every datetime ships in BOTH forms: ``*_utc`` (Unix seconds) and
``*_at`` (ISO 8601 UTC string). Phone numbers are only ever the MASKED form
Gumtree shows a logged-out visitor.
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
# Shared value objects
# =============================================================================


class Attribute(_BaseModel):
    """One listing attribute — e.g. ``vehicle_mileage`` = ``117628``."""

    key: str
    label: str | None = None
    value: str | None = None
    unit: str | None = None


class CategoryRef(_BaseModel):
    """A category reference attached to an autocomplete suggestion."""

    id: int | None = None
    name: str | None = None
    slug: str | None = None


class Breadcrumb(_BaseModel):
    """One step of a listing's category breadcrumb trail."""

    name: str | None = None
    url: str | None = None


class ListingSummary(_BaseModel):
    """A listing as it appears on a search / seller / similar-listings grid."""

    id: str
    title: str | None = None
    url: str | None = None
    description: str | None = Field(default=None, description="Gumtree's short description")
    price: float | None = Field(default=None, description="Numeric price in GBP")
    price_text: str | None = Field(default=None, description="Price as shown, e.g. '£1,850.00pm'")
    price_frequency: str | None = Field(default=None, description="pm / pw for rentals")
    currency: str = "GBP"
    location: str | None = None
    location_id: str | None = None
    postcode: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    distance_text: str | None = Field(
        default=None, description="e.g. '13 miles' from the search location"
    )
    distance_miles: float | None = None
    category_id: int | None = None
    category_name: str | None = None
    category_ids: list[int] = Field(default_factory=list, description="Root-to-leaf category ids")
    image_url: str | None = None
    image_urls: list[str] = Field(default_factory=list)
    image_count: int | None = None
    posted_text: str | None = Field(
        default=None, description="Relative age as shown, e.g. '3 days ago'"
    )
    posted_utc: float | None = None
    posted_at: str | None = None
    status: str | None = None
    seller_type: str | None = Field(default=None, description="Private / Trade / Agency")
    seller_id: str | None = None
    account_id: str | None = None
    is_pro_seller: bool | None = None
    is_featured: bool | None = Field(default=None, description="Paid top-slot ad")
    is_urgent: bool | None = None
    is_bumped_up: bool | None = None
    is_standout: bool | None = None
    is_premium: bool | None = None
    has_video: bool | None = None
    supports_shipping: bool | None = None
    favourite_count: int | None = None
    seller_skills: list[str] = Field(default_factory=list, description="Services listings only")
    attributes: list[Attribute] = Field(default_factory=list)


# =============================================================================
# Search
# =============================================================================


class CategoryFacet(_BaseModel):
    """A sub-category of a result set, with its listing count."""

    name: str | None = None
    slug: str | None = None
    count: int | None = None


class SearchResponse(_BaseModel):
    """Response from ``GET /v1/gumtree/search``."""

    query: str | None = None
    category: str | None = Field(default=None, description="Category slug the search ran in")
    category_name: str | None = None
    category_id: int | None = None
    location: str | None = Field(default=None, description="Location slug / postcode searched")
    location_name: str | None = None
    distance: float | None = None
    sort: str | None = None
    page: int = 1
    total_pages: int | None = None
    total_results: int | None = None
    result_count: int = 0
    listings: list[ListingSummary] = Field(default_factory=list)
    category_facets: list[CategoryFacet] = Field(
        default_factory=list, description="Sub-categories of the result set, with counts"
    )
    url: str | None = None


class FilterOption(_BaseModel):
    """One selectable value of a search filter, with its live result count."""

    label: str | None = None
    value: str | None = None
    count: int | None = None


class SearchFilter(_BaseModel):
    """One filter Gumtree offers for the category, as ``filters=key:value`` input."""

    key: str
    label: str | None = None
    type: str | None = Field(
        default=None,
        description="enum / multiple_selection / enum_range / range_freeform / boolean",
    )
    min_key: str | None = Field(default=None, description="Range filters: the lower-bound key")
    max_key: str | None = Field(default=None, description="Range filters: the upper-bound key")
    options: list[FilterOption] = Field(default_factory=list)
    min_options: list[FilterOption] = Field(default_factory=list)
    max_options: list[FilterOption] = Field(default_factory=list)


class SortOption(_BaseModel):
    """A sort order Gumtree offers for the category."""

    value: str
    label: str | None = None


class FiltersResponse(_BaseModel):
    """Response from ``GET /v1/gumtree/search/filters``."""

    category: str | None = None
    category_name: str | None = None
    total_results: int | None = None
    filters: list[SearchFilter] = Field(default_factory=list)
    sort_options: list[SortOption] = Field(default_factory=list)
    distance_options: list[float] = Field(
        default_factory=list, description="Radius values in miles"
    )
    category_facets: list[CategoryFacet] = Field(default_factory=list)


# =============================================================================
# Listing detail
# =============================================================================


class SellerRating(_BaseModel):
    """Seller star rating with a per-star breakdown (``"1"``..``"5"``)."""

    average: float | None = None
    total: int | None = None
    breakdown: dict[str, int] = Field(default_factory=dict)


class SellerVerification(_BaseModel):
    """Gumtree's business-verification status and the checks it passed."""

    status: str | None = None
    label: str | None = None
    checks: list[str] = Field(default_factory=list)


class Seller(_BaseModel):
    """The seller of a listing."""

    name: str | None = None
    user_id: str | None = None
    public_id: str | None = None
    type: str | None = Field(default=None, description="Private / Trade / Agency")
    is_pro: bool | None = None
    posting_since: str | None = Field(default=None, description="e.g. '6+ years'")
    last_active_utc: float | None = None
    last_active_at: str | None = None
    total_listings: int | None = None
    listings_last_year: int | None = None
    listings_by_category: dict[str, int] = Field(default_factory=dict)
    reply_speed: str | None = None
    reply_rate: str | None = None
    rating: SellerRating | None = None
    verification: SellerVerification | None = None
    phone_masked: str | None = Field(default=None, description="e.g. '0794997XXXX'")
    website_url: str | None = None
    avatar_url: str | None = None
    logo_url: str | None = None
    badges: list[str] = Field(default_factory=list)


class ListingDetail(_BaseModel):
    """Response from ``GET /v1/gumtree/listings/{listing_id}``."""

    id: str
    title: str | None = None
    url: str | None = None
    description: str | None = None
    price: float | None = None
    price_text: str | None = None
    price_frequency: str | None = None
    currency: str = "GBP"
    vat: str | None = Field(default=None, description="Motors trade listings: 'Inc VAT' / 'No VAT'")
    location: str | None = None
    area: str | None = None
    sub_area: str | None = None
    location_id: str | None = None
    postcode: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    category_id: int | None = None
    category_name: str | None = None
    category_ids: list[int] = Field(default_factory=list)
    breadcrumbs: list[Breadcrumb] = Field(default_factory=list)
    image_urls: list[str] = Field(default_factory=list)
    video_urls: list[str] = Field(default_factory=list)
    posted_text: str | None = None
    posted_utc: float | None = Field(default=None, description="Last (re)posted — moves on a bump")
    posted_at: str | None = None
    created_utc: float | None = Field(default=None, description="When the ad was first created")
    created_at: str | None = None
    updated_utc: float | None = None
    updated_at: str | None = None
    expires_at: str | None = Field(
        default=None, description="Date the ad is valid through (YYYY-MM-DD)"
    )
    is_featured: bool | None = None
    is_urgent: bool | None = None
    is_bumped_up: bool | None = None
    is_standout: bool | None = None
    favourite_count: int | None = None
    vehicle_history_checked: bool | None = Field(
        default=None, description="Motors: Gumtree's vehicle history check ran on this car"
    )
    attributes: list[Attribute] = Field(default_factory=list)
    seller: Seller | None = None
    seller_skills: list[str] = Field(default_factory=list, description="Services listings only")
    seller_listings_url: str | None = None
    similar_listings: list[ListingSummary] = Field(default_factory=list)


# =============================================================================
# Seller listings
# =============================================================================


class SellerListingsResponse(_BaseModel):
    """Response from ``GET /v1/gumtree/listings/{listing_id}/seller-listings``."""

    listing_id: str
    seller_name: str | None = None
    total_results: int | None = None
    page: int = 1
    total_pages: int | None = None
    result_count: int = 0
    listings: list[ListingSummary] = Field(default_factory=list)


# =============================================================================
# Reference data
# =============================================================================


class Suggestion(_BaseModel):
    """One search-box keyword suggestion."""

    query: str
    highlighted: str | None = None
    categories: list[CategoryRef] = Field(
        default_factory=list, description="Category path Gumtree attaches to the suggestion"
    )


class AutocompleteResponse(_BaseModel):
    """Response from ``GET /v1/gumtree/autocomplete``."""

    query: str
    result_count: int = 0
    suggestions: list[Suggestion] = Field(default_factory=list)


class LocationSuggestion(_BaseModel):
    """A Gumtree location matched by name or postcode prefix."""

    id: int | None = None
    name: str | None = None
    type: str | None = Field(default=None, description="location / outcode / postcode")
    latitude: float | None = None
    longitude: float | None = None


class LocationAutocompleteResponse(_BaseModel):
    """Response from ``GET /v1/gumtree/locations/autocomplete``."""

    query: str
    result_count: int = 0
    locations: list[LocationSuggestion] = Field(default_factory=list)


class TreeNode(_BaseModel):
    """A category or location node. ``slug`` is what ``search`` takes."""

    id: int
    name: str | None = None
    slug: str | None = None
    has_children: bool | None = None


class TreeResponse(_BaseModel):
    """Response from ``GET /v1/gumtree/categories`` and ``GET /v1/gumtree/locations``."""

    id: int
    name: str | None = None
    slug: str | None = None
    result_count: int = 0
    children: list[TreeNode] = Field(default_factory=list)
