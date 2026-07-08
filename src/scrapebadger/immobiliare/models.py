"""Pydantic models for Immobiliare API responses.

These models mirror the backend ``immobiliare_scraper`` response schema,
which normalises Immobiliare's internal ``api-next`` shapes into a clean,
market-agnostic snake_case schema. All models are immutable (frozen) and
ignore unknown fields for forward compatibility. Markets: it (immobiliare.it),
es (indomio.es), gr (indomio.gr), lu (immotop.lu) — all EUR.
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
# Shared nested models
# =============================================================================


class Photo(_BaseModel):
    """A single listing photo in three sizes."""

    id: int | None = None
    caption: str | None = None
    small: str | None = None
    medium: str | None = None
    large: str | None = None


class Price(_BaseModel):
    """A listing price (``price_per_sqm`` / ``loan_from`` are detail-only)."""

    value: int | None = None
    formatted: str | None = None
    min_value: str | None = None
    max_value: str | None = None
    currency: str = "EUR"
    visible: bool = True
    price_per_sqm: str | None = None
    loan_from: str | None = None


class Location(_BaseModel):
    """The geographic location block of a listing."""

    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    marker: str | None = None
    region: str | None = None
    province: str | None = None
    city: str | None = None
    macrozone: str | None = None
    microzone: str | None = None
    zipcode: str | None = None
    nation_code: str | None = None
    nation_name: str | None = None


class Feature(_BaseModel):
    """A single listing feature/amenity."""

    type: str | None = None
    label: str | None = None
    compact_label: str | None = None


class Agency(_BaseModel):
    """The advertising agency summary attached to a listing."""

    id: int | None = None
    type: str | None = None
    display_name: str | None = None
    label: str | None = None
    url: str | None = None
    is_paid: bool | None = None
    guaranteed: bool | None = None
    show_logo: bool | None = None
    image_small: str | None = None
    image_large: str | None = None
    phones: list[str] = Field(default_factory=list)


class Agent(_BaseModel):
    """The individual agent behind a listing."""

    type: str | None = None
    display_name: str | None = None
    label: str | None = None
    image_gender: str | None = None
    image_url: str | None = None
    phones: list[str] = Field(default_factory=list)


class PropertyUnit(_BaseModel):
    """One unit within a listing (a listing may bundle several — a 'project')."""

    is_main: bool = False
    surface: str | None = None
    surface_value: float | None = None
    rooms: str | None = None
    bathrooms: str | None = None
    bedrooms: str | None = None
    floor: str | None = None
    elevator: bool | None = None
    garage: str | None = None
    heating: str | None = None
    energy_class: str | None = None
    condominium_fees: str | None = None
    typology: str | None = None
    category: str | None = None
    caption: str | None = None
    description: str | None = None
    price: Price | None = None
    features: list[Feature] = Field(default_factory=list)
    ga4_features: list[str] = Field(default_factory=list)
    views: list[str] = Field(default_factory=list)
    photos: list[Photo] = Field(default_factory=list)


# =============================================================================
# Listing (search card + /listings/{id} detail)
# =============================================================================


class Listing(_BaseModel):
    """A normalised Immobiliare listing (search card or detail)."""

    id: int
    uuid: str | None = None
    url: str | None = None
    title: str | None = None
    contract: str | None = None  # "sale" | "rent"
    is_new: bool | None = None
    luxury: bool | None = None
    is_project: bool | None = None
    is_mosaic: bool | None = None
    visibility: str | None = None
    typology: str | None = None
    category: str | None = None
    price: Price | None = None
    location: Location | None = None
    # Flattened convenience fields (from the main property unit)
    surface: str | None = None
    rooms: str | None = None
    bathrooms: str | None = None
    floor: str | None = None
    energy_class: str | None = None
    description: str | None = None
    photo_count: int | None = None
    has_virtual_tour: bool | None = None
    photos: list[Photo] = Field(default_factory=list)
    agency: Agency | None = None
    agent: Agent | None = None
    properties_count: int | None = None
    properties: list[PropertyUnit] = Field(default_factory=list)
    # Detail-only fields (populated by GET /listings/{id})
    creation_date: str | None = None
    last_modified_utc: float | None = None
    last_modified_at: str | None = None
    features_full: list[Feature] = Field(default_factory=list)


# =============================================================================
# Agency profile (/agencies/{id})
# =============================================================================


class AgencyAgent(_BaseModel):
    """A single agent on an agency profile."""

    id: int | None = None
    name: str | None = None
    surname: str | None = None
    gender: str | None = None
    thumbnail: str | None = None


class AgencyProfile(_BaseModel):
    """Full agency/advertiser profile (rendered from the agency page)."""

    id: int
    type: str | None = None
    name: str | None = None
    url: str | None = None
    address: str | None = None
    description: str | None = None
    website: str | None = None
    image: str | None = None
    is_paid: bool | None = None
    partnership: str | None = None
    real_estate_ads: int | None = None
    real_estate_sales: int | None = None
    region: str | None = None
    province: str | None = None
    city: str | None = None
    macrozone: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    phones: list[str] = Field(default_factory=list)
    opening_hours: list[str] = Field(default_factory=list)
    agents: list[AgencyAgent] = Field(default_factory=list)
    market: str = "it"


# =============================================================================
# Autocomplete (/autocomplete)
# =============================================================================


class Suggestion(_BaseModel):
    """A geography autocomplete candidate → usable as a search location."""

    id: str | None = None
    label: str | None = None
    type: str | None = None  # nation | region | province | comune | zone
    region_id: str | None = None
    province_id: str | None = None
    city_id: str | None = None
    macrozone_ids: list[str] = Field(default_factory=list)
    url: str | None = None


# =============================================================================
# Market insights (/market-insights/prices)
# =============================================================================


class PriceStatsPoint(_BaseModel):
    """One point in the €/m² time series."""

    label: str
    value: float | None = None


# =============================================================================
# Markets (/markets)
# =============================================================================


class Market(_BaseModel):
    """A single supported Immobiliare-group market."""

    code: str
    domain: str
    country_code: str
    locale: str
    currency: str
    name: str


# =============================================================================
# Response envelopes
# =============================================================================


class RelatedSearch(_BaseModel):
    """A related-search suggestion returned alongside search results."""

    label: str | None = None
    url: str | None = None


class SuggestResponse(_BaseModel):
    """Response for /autocomplete."""

    suggestions: list[Suggestion] = Field(default_factory=list)
    market: str = "it"


class SearchResponse(_BaseModel):
    """Response for /search."""

    listings: list[Listing] = Field(default_factory=list)
    count: int | None = None
    total_ads: int | None = None
    current_page: int | None = None
    max_pages: int | None = None
    is_results_limit_reached: bool | None = None
    agencies: list[Agency] = Field(default_factory=list)
    related_searches: list[RelatedSearch] = Field(default_factory=list)
    market: str = "it"
    source: str = "api"


class AgencyListingsResponse(_BaseModel):
    """Response for /agencies/{id}/listings."""

    agency_id: int
    listings: list[Listing] = Field(default_factory=list)
    count: int | None = None
    page: int = 1
    market: str = "it"


class PriceStatsResponse(_BaseModel):
    """Response for /market-insights/prices (€/m² time series)."""

    contract: str
    unit: str = "EUR/m²"
    points: list[PriceStatsPoint] = Field(default_factory=list)
    market: str = "it"


class ReferenceResponse(_BaseModel):
    """Response for /reference (filter enums accepted by /search)."""

    contracts: list[str] = Field(default_factory=list)
    categories: list[str] = Field(default_factory=list)
    sorts: list[str] = Field(default_factory=list)
