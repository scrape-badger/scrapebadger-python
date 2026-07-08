"""Pydantic models for LoopNet API responses.

These models mirror the backend ``loopnet_scraper`` response schema
field-for-field. All models are immutable (frozen) and ignore unknown fields
for forward compatibility. Every datetime field ships in BOTH ``*_utc`` (Unix
float) and ``*_at`` (ISO-8601 Z string).

LoopNet is multi-market (us/ca/uk/fr/es); every search response carries
``market`` + ``currency`` so a caller can tell CAD from GBP. Prices ship both
raw text (``price_text``) and parsed numeric (``price``) because CRE pricing
is heterogeneous ($/SF/YR, $/AC, total, "Contact").
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


class Broker(_BaseModel):
    """A LoopNet broker/agent attributed to a listing or profile."""

    name: str | None = None
    company: str | None = None
    title: str | None = None
    phone: str | None = None
    email: str | None = None
    photo: str | None = None
    url: str | None = None
    broker_id: str | None = None
    city: str | None = None
    region: str | None = None


class Space(_BaseModel):
    """One leasable space / unit within a listing (lease listings)."""

    name: str | None = None
    space_use: str | None = None
    size_sqft: int | None = None
    size_text: str | None = None
    rent_text: str | None = None
    rent_per_sqft: float | None = None
    rent_period: str | None = None
    term: str | None = None
    condition: str | None = None
    available_date: str | None = None
    floor: str | None = None


class MarketInfo(_BaseModel):
    """A supported coverage market (for /markets)."""

    code: str
    domain: str
    country: str
    currency: str
    locale: str
    name: str


class PropertyTypeInfo(_BaseModel):
    """A LoopNet property-type facet (for /property-types)."""

    slug: str
    name: str


class Pagination(_BaseModel):
    """Page-number pagination (LoopNet returns ~25 cards per page, caps ~500)."""

    current_page: int = 1
    per_page: int | None = None
    total_pages: int | None = None
    total_results: int | None = None


# =============================================================================
# Search results
# =============================================================================


class ListingCard(_BaseModel):
    """One LoopNet search result card (search / broker listings)."""

    position: int
    listing_id: str | None = None
    property_id: str | None = None
    url: str | None = None
    # Taxonomy
    listing_type: str | None = None
    property_type: str | None = None
    property_type_id: str | None = None
    space_use: str | None = None
    status: str | None = None
    status_id: str | None = None
    exposure_level: str | None = None
    is_auction: bool | None = None
    # Content
    title: str | None = None
    subtitle: str | None = None
    description: str | None = None
    building_rating: float | None = None
    year_built: int | None = None
    # Price
    price_text: str | None = None
    price: float | None = None
    price_currency: str | None = None
    price_period: str | None = None
    # Size
    size_text: str | None = None
    size_min_sqft: int | None = None
    size_max_sqft: int | None = None
    # Address
    address: str | None = None
    city: str | None = None
    state: str | None = None
    zip: str | None = None
    county: str | None = None
    country: str | None = None
    market_id: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    # Media / meta
    thumbnail: str | None = None
    has_virtual_tour: bool | None = None
    page_rank: int | None = None
    position_rank: int | None = None
    brokers: list[Broker] = Field(default_factory=list)


# =============================================================================
# Listing detail
# =============================================================================


class ListingDetail(_BaseModel):
    """Full LoopNet listing detail (JSON-LD RealEstateListing + DOM facts)."""

    # Identity
    listing_id: str | None = None
    property_id: str | None = None
    url: str | None = None
    market: str | None = None
    country: str | None = None
    listing_type: str | None = None
    transaction_type: str | None = None
    # Content
    name: str | None = None
    title: str | None = None
    subtitle: str | None = None
    description: str | None = None
    highlights: list[str] = Field(default_factory=list)
    # Price
    price_text: str | None = None
    price: float | None = None
    price_currency: str | None = None
    price_period: str | None = None
    rental_rate_text: str | None = None
    cap_rate: float | None = None
    noi: str | None = None
    price_per_sqft: float | None = None
    # Building / property facts
    property_type: str | None = None
    property_sub_type: str | None = None
    building_class: str | None = None
    building_size_sqft: int | None = None
    building_size_text: str | None = None
    rentable_building_area: str | None = None
    total_space_available: str | None = None
    total_space_available_sqft: int | None = None
    min_divisible: str | None = None
    max_contiguous: str | None = None
    typical_floor_size: str | None = None
    building_height: str | None = None
    ceiling_height: str | None = None
    year_built: int | None = None
    year_built_renovated: str | None = None
    building_rating: float | None = None
    lot_size_text: str | None = None
    lot_size_acres: float | None = None
    units: int | None = None
    stories: int | None = None
    percent_leased: str | None = None
    tenancy: str | None = None
    zoning: str | None = None
    parcel_id: str | None = None
    parking: str | None = None
    walk_score: int | None = None
    amenities: list[str] = Field(default_factory=list)
    # Address / geo
    address: str | None = None
    city: str | None = None
    state: str | None = None
    zip: str | None = None
    county: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    # Media
    images: list[str] = Field(default_factory=list)
    photo_count: int | None = None
    videos: list[str] = Field(default_factory=list)
    documents: list[str] = Field(default_factory=list)
    has_virtual_tour: bool | None = None
    # Spaces (lease) + brokers
    spaces: list[Space] = Field(default_factory=list)
    brokers: list[Broker] = Field(default_factory=list)
    # Every additionalProperty name/value pair LoopNet ships, verbatim
    additional_facts: list[dict[str, str]] = Field(default_factory=list)
    # Timing
    date_posted_utc: float | None = None
    date_posted_at: str | None = None
    date_updated_utc: float | None = None
    date_updated_at: str | None = None
    scraped_utc: float | None = None
    scraped_at: str | None = None


# =============================================================================
# Broker profile
# =============================================================================


class BrokerProfile(_BaseModel):
    """A LoopNet broker/professional profile with their listings."""

    broker_id: str | None = None
    name: str | None = None
    company: str | None = None
    title: str | None = None
    phone: str | None = None
    email: str | None = None
    photo: str | None = None
    url: str | None = None
    bio: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    license_number: str | None = None
    specialties: list[str] = Field(default_factory=list)
    listing_count: int | None = None
    listings: list[ListingCard] = Field(default_factory=list)
    scraped_utc: float | None = None
    scraped_at: str | None = None


# =============================================================================
# Response envelopes
# =============================================================================


class SearchResponse(_BaseModel):
    """Response for /search."""

    market: str
    country: str
    currency: str
    listing_type: str
    property_type: str | None = None
    location: str | None = None
    results: list[ListingCard] = Field(default_factory=list)
    pagination: Pagination = Field(default_factory=Pagination)
    scraped_utc: float | None = None
    scraped_at: str | None = None


class ListingResponse(_BaseModel):
    """Response for /listings/{listing_id}."""

    listing: ListingDetail


class BrokerResponse(_BaseModel):
    """Response for /brokers/{slug}/{broker_id}."""

    broker: BrokerProfile


class MarketsResponse(_BaseModel):
    """Response for /markets."""

    markets: list[MarketInfo] = Field(default_factory=list)


class PropertyTypesResponse(_BaseModel):
    """Response for /property-types."""

    property_types: list[PropertyTypeInfo] = Field(default_factory=list)
