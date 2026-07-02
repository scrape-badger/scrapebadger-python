"""Pydantic models for Realtor API responses.

These models mirror the backend ``realtor_scraper`` response schema
field-for-field. All models are immutable (frozen) and ignore unknown fields
for forward compatibility. Every datetime field ships in BOTH ``*_utc`` (Unix
float) and ``*_at`` (ISO-8601 Z string).
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
# Shared / nested models
# =============================================================================


class Coordinate(_BaseModel):
    """A latitude/longitude pair."""

    lat: float | None = None
    lon: float | None = None


class Phone(_BaseModel):
    """A single phone number for an agent or office."""

    number: str | None = None
    type: str | None = None
    ext: str | None = None
    primary: bool | None = None


class Address(_BaseModel):
    """A property street address."""

    line: str | None = None
    city: str | None = None
    state: str | None = None
    state_code: str | None = None
    postal_code: str | None = None
    country: str | None = None
    neighborhood: str | None = None
    county: str | None = None
    coordinate: Coordinate | None = None


class Photo(_BaseModel):
    """A single listing photo with resolution variants."""

    href: str | None = None
    href_high: str | None = None
    href_med: str | None = None
    href_low: str | None = None
    tags: list[str] = Field(default_factory=list)
    description: str | None = None


class Office(_BaseModel):
    """The brokerage office an agent belongs to."""

    name: str | None = None
    email: str | None = None
    href: str | None = None
    logo: str | None = None
    phones: list[Phone] = Field(default_factory=list)
    address: Address | None = None


class Agent(_BaseModel):
    """A listing agent (with office/broker contacts)."""

    agent_id: str | None = None
    name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    title: str | None = None
    type: str | None = None
    email: str | None = None
    phones: list[Phone] = Field(default_factory=list)
    photo: str | None = None
    href: str | None = None
    office: Office | None = None
    broker: str | None = None
    nrds_id: str | None = None
    state_license: str | None = None


class OpenHouse(_BaseModel):
    """A single scheduled open house."""

    start_utc: str | None = None
    start_at: str | None = None
    end_utc: str | None = None
    end_at: str | None = None
    description: str | None = None
    time_zone: str | None = None
    href: str | None = None


class School(_BaseModel):
    """A school associated with a property."""

    name: str | None = None
    rating: float | None = None
    education_levels: list[str] = Field(default_factory=list)
    grades: str | None = None
    distance_miles: float | None = None
    district: str | None = None


class TaxRecord(_BaseModel):
    """A single year of tax/assessment history."""

    year: int | None = None
    tax: float | None = None
    assessment_building: float | None = None
    assessment_land: float | None = None
    assessment_total: float | None = None


class PriceEvent(_BaseModel):
    """A single price-history event (listing, sale, price change)."""

    date_utc: str | None = None
    date_at: str | None = None
    event: str | None = None
    price: float | None = None
    price_per_sqft: float | None = None
    source_listing_id: str | None = None


class Estimate(_BaseModel):
    """A third-party value estimate for a property."""

    source: str | None = None
    estimate: float | None = None
    estimate_high: float | None = None
    estimate_low: float | None = None
    date_utc: str | None = None
    date_at: str | None = None


class DetailGroup(_BaseModel):
    """A named group of free-text detail lines (e.g. "Interior Features")."""

    category: str | None = None
    text: list[str] = Field(default_factory=list)


class Flags(_BaseModel):
    """Boolean status flags for a listing."""

    is_new_listing: bool | None = None
    is_pending: bool | None = None
    is_contingent: bool | None = None
    is_foreclosure: bool | None = None
    is_new_construction: bool | None = None
    is_price_reduced: bool | None = None
    is_coming_soon: bool | None = None


# =============================================================================
# Property (search card) and PropertyDetail
# =============================================================================


class Property(_BaseModel):
    """A property listing (search result card)."""

    property_id: str | None = None
    listing_id: str | None = None
    mls_number: str | None = None
    market: str | None = None
    country: str | None = None
    url: str | None = None
    status: str | None = None
    transaction_type: str | None = None
    currency: str | None = None
    list_price: float | None = None
    list_price_formatted: str | None = None
    list_price_min: float | None = None
    list_price_max: float | None = None
    price_per_sqft: float | None = None
    price_reduced_amount: float | None = None
    last_sold_price: float | None = None
    last_sold_date_utc: str | None = None
    last_sold_date_at: str | None = None
    hoa_fee: float | None = None
    property_type: str | None = None
    sub_type: str | None = None
    beds: float | None = None
    baths: float | None = None
    baths_full: float | None = None
    baths_half: float | None = None
    sqft: float | None = None
    lot_sqft: float | None = None
    year_built: int | None = None
    stories: float | None = None
    garage: float | None = None
    rooms: float | None = None
    parking_spaces: float | None = None
    address: Address | None = None
    description_text: str | None = None
    primary_photo: str | None = None
    photo_count: int | None = None
    photos: list[Photo] = Field(default_factory=list)
    virtual_tours: list[str] = Field(default_factory=list)
    videos: list[str] = Field(default_factory=list)
    flags: Flags | None = None
    tags: list[str] = Field(default_factory=list)
    list_date_utc: str | None = None
    list_date_at: str | None = None
    last_update_utc: str | None = None
    last_update_at: str | None = None
    days_on_market: int | None = None
    agents: list[Agent] = Field(default_factory=list)
    source_mls_id: str | None = None
    source_mls_name: str | None = None
    open_houses: list[OpenHouse] = Field(default_factory=list)


class PropertyDetail(Property):
    """Full property detail (/properties/{property_id}).

    Extends :class:`Property` with the heavy detail blocks that are only
    returned on the single-property endpoint.
    """

    details: list[DetailGroup] = Field(default_factory=list)
    amenities: list[str] = Field(default_factory=list)
    tax_history: list[TaxRecord] = Field(default_factory=list)
    price_history: list[PriceEvent] = Field(default_factory=list)
    schools: list[School] = Field(default_factory=list)
    estimates: list[Estimate] = Field(default_factory=list)


# =============================================================================
# Autocomplete
# =============================================================================


class Suggestion(_BaseModel):
    """A single autocomplete suggestion (location or address)."""

    id: str | None = None
    type: str | None = None
    label: str | None = None
    city: str | None = None
    state_code: str | None = None
    postal_code: str | None = None
    country: str | None = None
    slug_id: str | None = None
    geo_id: str | None = None
    coordinate: Coordinate | None = None
    market: str | None = None


# =============================================================================
# Reference
# =============================================================================


class MarketInfo(_BaseModel):
    """A single supported marketplace (for /markets)."""

    code: str
    domain: str
    country: str
    currency: str
    locale: str
    name: str


# =============================================================================
# Response envelopes
# =============================================================================


class AutocompleteResponse(_BaseModel):
    """Response for /autocomplete."""

    market: str
    query: str
    suggestions: list[Suggestion] = Field(default_factory=list)


class SearchResponse(_BaseModel):
    """Response for /search."""

    market: str
    country: str | None = None
    total: int | None = None
    count: int | None = None
    page: int | None = None
    total_pages: int | None = None
    results: list[Property] = Field(default_factory=list)


class MarketsResponse(_BaseModel):
    """Response for /markets."""

    markets: list[MarketInfo] = Field(default_factory=list)
