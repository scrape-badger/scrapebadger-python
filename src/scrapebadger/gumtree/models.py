"""Pydantic models for Gumtree API responses.

These models mirror the backend ``gumtree_scraper`` response schema
field-for-field. All models are immutable (frozen) and ignore unknown fields
for forward compatibility.

Three markets share these models: ``uk`` (gumtree.com, GBP), ``au``
(gumtree.com.au, AUD) and ``za`` (gumtree.co.za, ZAR). They are separate
platforms, so a field one market does not publish is simply ``None`` there.
Category, location and tree ids are ints on uk/au and gumtree.co.za refs
(strings such as ``"p6dnh"``) on za, so those fields are ``int | str``.
Every top-level response carries the ``market`` it came from. Every datetime
ships in BOTH forms: ``*_utc`` (Unix seconds) and ``*_at`` (ISO 8601 UTC
string). Phone numbers are only ever the MASKED form Gumtree shows a
logged-out visitor.
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

    id: int | str | None = Field(default=None, description="za: a ref such as 'p6dnh'")
    name: str | None = None
    slug: str | None = None


class Breadcrumb(_BaseModel):
    """One step of a listing's category breadcrumb trail."""

    name: str | None = None
    url: str | None = None


class ListingSummary(_BaseModel):
    """A listing as it appears on a search / seller / similar-listings grid."""

    id: str
    short_id: str | None = Field(
        default=None, description="Not published by any market at present (za's old short id)"
    )
    title: str | None = None
    url: str | None = None
    description: str | None = Field(default=None, description="Gumtree's short description")
    price: float | None = Field(default=None, description="Numeric price in `currency`")
    price_text: str | None = Field(default=None, description="Price as shown, e.g. '£1,850.00pm'")
    price_frequency: str | None = Field(default=None, description="pm / pw for rentals")
    price_type: str | None = Field(
        default=None, description="au: FIXED, NEGOTIABLE, FREE, SWAP_TRADE…; za: ASKING_PRICE, POA…"
    )
    currency: str = "GBP"
    location: str | None = None
    location_id: str | None = None
    postcode: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    distance_text: str | None = Field(
        default=None, description="e.g. '13 miles' (uk) or '4 km' (au) from the search location"
    )
    distance_miles: float | None = None
    category_id: int | str | None = Field(default=None, description="za: a ref such as 'p6dnh'")
    category_name: str | None = None
    category_ids: list[int | str] = Field(
        default_factory=list, description="Root-to-leaf category ids (refs on za)"
    )
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
    seller_name: str | None = None
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

    id: int | str | None = Field(
        default=None, description="au: the numeric category id `search` takes; za: its ref"
    )
    name: str | None = None
    slug: str | None = None
    count: int | None = None


class SearchResponse(_BaseModel):
    """Response from ``GET /v1/gumtree/search``."""

    market: str = Field(
        default="uk", description="uk = gumtree.com, au = gumtree.com.au, za = gumtree.co.za"
    )
    query: str | None = None
    category: str | None = Field(default=None, description="Category slug the search ran in")
    category_name: str | None = None
    category_id: int | str | None = Field(default=None, description="za: a ref such as 'p6dnh'")
    location: str | None = Field(default=None, description="Location slug / postcode searched")
    location_name: str | None = None
    distance: float | None = None
    sort: str | None = None
    page: int = 1
    total_pages: int | None = None
    total_results: int | None = None
    result_count: int = 0
    currency: str = Field(default="GBP", description="Currency of every price in the results")
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

    market: str = Field(
        default="uk", description="uk = gumtree.com, au = gumtree.com.au, za = gumtree.co.za"
    )
    category: str | None = None
    category_name: str | None = None
    total_results: int | None = None
    filters: list[SearchFilter] = Field(default_factory=list)
    sort_options: list[SortOption] = Field(default_factory=list)
    distance_options: list[float] = Field(
        default_factory=list, description="Radius values: miles (uk) or km (au)"
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
    member_since_year: int | None = Field(
        default=None, description="au/za: year the account opened"
    )
    last_active_text: str | None = Field(default=None, description="au: e.g. 'yesterday'")
    last_active_utc: float | None = None
    last_active_at: str | None = None
    total_listings: int | None = Field(default=None, description="Live listings right now")
    lifetime_listings: int | None = Field(
        default=None, description="Ads ever posted (no market publishes it at present)"
    )
    total_views: int | None = Field(
        default=None, description="Views across all their ads (no market publishes it at present)"
    )
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

    market: str = Field(
        default="uk", description="uk = gumtree.com, au = gumtree.com.au, za = gumtree.co.za"
    )
    id: str
    title: str | None = None
    url: str | None = None
    description: str | None = None
    price: float | None = None
    price_text: str | None = None
    price_frequency: str | None = None
    price_type: str | None = Field(
        default=None, description="au: FIXED, NEGOTIABLE, FREE, SWAP_TRADE…; za: ASKING_PRICE, POA…"
    )
    currency: str = "GBP"
    vat: str | None = Field(default=None, description="Motors trade listings: 'Inc VAT' / 'No VAT'")
    location: str | None = None
    area: str | None = None
    sub_area: str | None = None
    location_id: str | None = None
    postcode: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    category_id: int | str | None = Field(default=None, description="za: a ref such as 'p6dnh'")
    category_name: str | None = None
    category_ids: list[int | str] = Field(default_factory=list)
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
    status: str | None = None
    view_count: int | None = Field(default=None, description="au/za: views of this ad")
    reply_count: int | None = Field(default=None, description="au: replies to this ad")
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

    market: str = Field(
        default="uk", description="uk = gumtree.com, au = gumtree.com.au, za = gumtree.co.za"
    )
    listing_id: str
    seller_name: str | None = None
    total_results: int | None = None
    page: int = 1
    total_pages: int | None = None
    has_next: bool | None = Field(default=None, description="za: another page follows")
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

    market: str = Field(
        default="uk", description="uk = gumtree.com, au = gumtree.com.au, za = gumtree.co.za"
    )
    query: str
    result_count: int = 0
    suggestions: list[Suggestion] = Field(default_factory=list)


class LocationSuggestion(_BaseModel):
    """A Gumtree location matched by name or postcode prefix."""

    id: int | str | None = Field(default=None, description="za: a ref such as 'pfw8k'")
    name: str | None = None
    type: str | None = Field(
        default=None, description="uk: location / outcode / postcode; au/za: region / area"
    )
    latitude: float | None = None
    longitude: float | None = None


class LocationAutocompleteResponse(_BaseModel):
    """Response from ``GET /v1/gumtree/locations/autocomplete``."""

    market: str = Field(
        default="uk", description="uk = gumtree.com, au = gumtree.com.au, za = gumtree.co.za"
    )
    query: str
    result_count: int = 0
    locations: list[LocationSuggestion] = Field(default_factory=list)


class TreeNode(_BaseModel):
    """A category or location node. ``slug`` (uk) or ``id`` (au/za) is what ``search`` takes."""

    id: int | str = Field(description="int on uk/au, a ref such as 'p6dnh' on za")
    name: str | None = None
    slug: str | None = None
    has_children: bool | None = None


class TreeResponse(_BaseModel):
    """Response from ``GET /v1/gumtree/categories`` and ``GET /v1/gumtree/locations``."""

    market: str = Field(
        default="uk", description="uk = gumtree.com, au = gumtree.com.au, za = gumtree.co.za"
    )
    id: int | str = Field(description="int on uk/au, a ref such as 'p6dnh' on za")
    name: str | None = None
    slug: str | None = None
    result_count: int = 0
    children: list[TreeNode] = Field(default_factory=list)


# =============================================================================
# Markets
# =============================================================================


class MarketInfo(_BaseModel):
    """One Gumtree site this API covers."""

    market: str = Field(description="uk / au / za — the `market` every method takes")
    domain: str
    country: str = Field(description="ISO country code, e.g. 'GB'")
    currency: str
    distance_unit: str | None = Field(
        default=None, description="Unit of the search `distance` (None: radius not offered)"
    )
    page_size: int = Field(description="Organic results per search page")
    id_format: str = Field(description="How search takes `category` and `location`")


class MarketsResponse(_BaseModel):
    """Response from ``GET /v1/gumtree/markets``."""

    result_count: int = 0
    markets: list[MarketInfo] = Field(default_factory=list)
