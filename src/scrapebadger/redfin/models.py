"""Pydantic models for Redfin API responses.

These models mirror the backend ``redfin_scraper`` response schema
field-for-field. All models are immutable (frozen) and ignore unknown fields
for forward compatibility.

Redfin is a single-domain, single-locale target (redfin.com, USD, en-US behind
a US residential IP), so there is no market/currency dimension on the models.
Every datetime field ships in BOTH ``*_utc`` (Unix float seconds) and ``*_at``
(ISO-8601 Z string).
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
# Shared
# =============================================================================


class LatLong(_BaseModel):
    latitude: float | None = None
    longitude: float | None = None


class Pagination(_BaseModel):
    current_page: int = 1
    per_page: int | None = None
    total_results: int | None = None


class MapBounds(_BaseModel):
    """Map bounding box a search covers."""

    north: float | None = None
    east: float | None = None
    south: float | None = None
    west: float | None = None


class RegionSelection(_BaseModel):
    """The geocoded region a search resolved to (name + centre point)."""

    name: str | None = None
    display_name: str | None = None
    type: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class SearchMedian(_BaseModel):
    """Median stats over the result set."""

    price: int | None = None
    sqft: int | None = None
    price_per_sqft: int | None = None
    dom: int | None = None
    beds: float | None = None
    baths: float | None = None


class DataSource(_BaseModel):
    """MLS attribution."""

    id: int | None = None
    name: str | None = None
    description: str | None = None


class Sash(_BaseModel):
    """A listing badge — "Open House", "New", "3D Tour"…"""

    type_id: int | None = None
    name: str | None = None
    color: str | None = None
    text: str | None = None


class MarketInfo(_BaseModel):
    """A supported coverage region (for /markets)."""

    code: str
    country: str
    currency: str
    locale: str
    name: str
    domain: str


# =============================================================================
# Search results
# =============================================================================


class Listing(_BaseModel):
    """One Redfin GIS search card."""

    position: int
    property_id: int | None = None
    listing_id: int | None = None
    building_id: int | None = None
    url: str | None = None
    # Status / type
    mls_id: str | None = None
    mls_status: str | None = None
    search_status: int | None = None
    property_type: int | None = None
    ui_property_type: int | None = None
    listing_type: int | None = None
    is_redfin: bool | None = None
    is_new_construction: bool | None = None
    is_hot: bool | None = None
    # Price / valuation
    price: int | None = None
    price_per_sqft: int | None = None
    hoa: int | None = None
    is_hoa_frequency_known: bool | None = None
    # Specs
    beds: float | None = None
    baths: float | None = None
    full_baths: int | None = None
    partial_baths: int | None = None
    sqft: int | None = None
    lot_size: int | None = None
    stories: float | None = None
    year_built: int | None = None
    parking_spaces: int | None = None
    # Address
    street_line: str | None = None
    unit_number: str | None = None
    city: str | None = None
    state: str | None = None
    zip: str | None = None
    country_code: str | None = None
    neighborhood: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    show_address_on_map: bool | None = None
    # Listing meta / timing
    days_on_market: int | None = None
    time_on_redfin_ms: int | None = None
    time_zone: str | None = None
    sold_date_utc: float | None = None
    sold_date_at: str | None = None
    listing_agent_name: str | None = None
    listing_agent_id: int | None = None
    listing_broker_name: str | None = None
    listing_broker_is_redfin: bool | None = None
    # Content
    listing_remarks: str | None = None
    key_facts: list[str] = Field(default_factory=list)
    listing_tags: list[str] = Field(default_factory=list)
    hotness_message: str | None = None
    sashes: list[Sash] = Field(default_factory=list)
    # Media
    num_pictures: int | None = None
    photo_format: str | None = None
    primary_photo: str | None = None
    has_virtual_tour: bool | None = None
    has_video_tour: bool | None = None
    has_3d_tour: bool | None = None
    tour_url: str | None = None
    open_house_start_utc: float | None = None
    open_house_start_at: str | None = None
    open_house_end_utc: float | None = None
    open_house_end_at: str | None = None
    open_house_text: str | None = None


# =============================================================================
# Property detail nested
# =============================================================================


class Address(_BaseModel):
    street_address: str | None = None
    unit_number: str | None = None
    city: str | None = None
    state: str | None = None
    zip: str | None = None
    county: str | None = None
    neighborhood: str | None = None
    country_code: str | None = None


class PriceHistoryEvent(_BaseModel):
    date: str | None = None
    date_utc: float | None = None
    date_at: str | None = None
    event: str | None = None
    price: int | None = None
    price_per_sqft: int | None = None
    source: str | None = None
    source_id: str | None = None
    mls_status: str | None = None


class TaxHistoryEvent(_BaseModel):
    year: int | None = None
    tax: int | None = None
    assessment_total: int | None = None
    assessment_land: int | None = None
    assessment_improvement: int | None = None


class School(_BaseModel):
    name: str | None = None
    rating: int | None = None
    grades: str | None = None
    level: str | None = None
    type: str | None = None
    distance: float | None = None
    num_students: int | None = None
    url: str | None = None


class Photo(_BaseModel):
    url: str | None = None
    caption: str | None = None


class AmenityGroup(_BaseModel):
    """One ``amenitiesInfo`` super-group → group → referenceName/content."""

    title: str | None = None
    items: list[dict[str, Any]] = Field(default_factory=list)


class Property(_BaseModel):
    """Full Redfin property detail."""

    # Identity
    property_id: int
    listing_id: int | None = None
    url: str | None = None
    mls_id: str | None = None
    mls_status: str | None = None
    property_type: str | None = None
    ui_property_type: int | None = None
    listing_type: int | None = None
    is_redfin: bool | None = None
    is_new_construction: bool | None = None
    # Price / valuation
    price: int | None = None
    price_per_sqft: int | None = None
    list_price: int | None = None
    sold_price: int | None = None
    last_sold_date_utc: float | None = None
    last_sold_date_at: str | None = None
    redfin_estimate: int | None = None
    rent_estimate: int | None = None
    hoa_fee: int | None = None
    hoa_frequency: str | None = None
    tax_annual: int | None = None
    # Specs
    beds: float | None = None
    baths: float | None = None
    full_baths: int | None = None
    partial_baths: int | None = None
    sqft: int | None = None
    lot_sqft: int | None = None
    stories: float | None = None
    year_built: int | None = None
    year_renovated: int | None = None
    days_on_market: int | None = None
    parking_spaces: int | None = None
    parking_type: str | None = None
    style: str | None = None
    # Location
    latitude: float | None = None
    longitude: float | None = None
    address: Address | None = None
    time_zone: str | None = None
    apn: str | None = None
    county: str | None = None
    # Content
    description: str | None = None
    key_facts: list[str] = Field(default_factory=list)
    listing_tags: list[str] = Field(default_factory=list)
    # Media
    photos: list[Photo] = Field(default_factory=list)
    num_photos: int | None = None
    has_3d_tour: bool | None = None
    has_video_tour: bool | None = None
    tour_url: str | None = None
    # Agent / broker
    listing_agent_name: str | None = None
    listing_agent_id: int | None = None
    listing_broker_name: str | None = None
    listing_broker_phone: str | None = None
    # Nested collections
    price_history: list[PriceHistoryEvent] = Field(default_factory=list)
    tax_history: list[TaxHistoryEvent] = Field(default_factory=list)
    schools: list[School] = Field(default_factory=list)
    amenities: list[AmenityGroup] = Field(default_factory=list)
    # Timestamps
    scraped_utc: float | None = None
    scraped_at: str | None = None


# =============================================================================
# Agent profile
# =============================================================================


class AgentReview(_BaseModel):
    rating: int | None = None
    comment: str | None = None
    date: str | None = None
    reviewer_name: str | None = None
    reviewer_type: str | None = None


class Agent(_BaseModel):
    """A Redfin real-estate agent profile."""

    agent_id: str | None = None
    name: str | None = None
    url: str | None = None
    profile_photo: str | None = None
    title: str | None = None
    is_redfin_agent: bool | None = None
    phone: str | None = None
    email: str | None = None
    brokerage: str | None = None
    bio: str | None = None
    rating: float | None = None
    review_count: int | None = None
    deals_last_year: int | None = None
    total_deals: int | None = None
    price_range_min: int | None = None
    price_range_max: int | None = None
    years_experience: int | None = None
    service_areas: list[str] = Field(default_factory=list)
    specialties: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    reviews: list[AgentReview] = Field(default_factory=list)
    listings: list[Listing] = Field(default_factory=list)
    scraped_utc: float | None = None
    scraped_at: str | None = None


# =============================================================================
# Autocomplete
# =============================================================================


class AutocompleteResult(_BaseModel):
    """A geocoded place suggestion for a search term (name + centre + bbox)."""

    name: str | None = None
    display_name: str | None = None
    type: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    north: float | None = None
    south: float | None = None
    east: float | None = None
    west: float | None = None


# =============================================================================
# Response envelopes
# =============================================================================


class SearchResponse(_BaseModel):
    location: str | None = None
    status: str = "for_sale"
    results: list[Listing] = Field(default_factory=list)
    total_results: int = 0
    region: RegionSelection | None = None
    map_bounds: MapBounds | None = None
    search_median: SearchMedian | None = None
    data_sources: list[DataSource] = Field(default_factory=list)
    pagination: Pagination = Field(default_factory=Pagination)
    scraped_utc: float | None = None
    scraped_at: str | None = None


class PropertyResponse(_BaseModel):
    property: Property


class AgentResponse(_BaseModel):
    agent: Agent


class AutocompleteResponse(_BaseModel):
    query: str
    results: list[AutocompleteResult] = Field(default_factory=list)


class MarketsResponse(_BaseModel):
    markets: list[MarketInfo] = Field(default_factory=list)
