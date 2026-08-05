"""Pydantic models for Apartments.com API responses.

These mirror the backend ``apartments_scraper`` response schema field-for-field.
All models are immutable (frozen) and ignore unknown fields for forward
compatibility.

apartments.com is a single-domain, single-locale target (US, USD, en-US behind
a US residential IP), so there is no market/currency dimension. There are also
no datetime fields: availability is rendered as free text with no year ("Now",
"Sep 3"), so the platform's ``*_utc``/``*_at`` convention does not apply.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class _BaseModel(BaseModel):
    """Base model with common configuration."""

    model_config = ConfigDict(frozen=True, extra="ignore")


class Unit(_BaseModel):
    """A single rentable unit within a floor plan."""

    unit_number: str | None = None
    unit_key: str | None = None
    rental_key: str | None = None
    model_key: str | None = None
    beds: float | None = None
    baths: float | None = None
    #: The advertised rent, from the rendered price column. Use THIS.
    rent: int | None = None
    rent_price_text: str | None = None
    #: Raw ``data-maxrent`` — measures roughly 2x the advertised rent and looks
    #: like an upper bound across lease terms. Exposed unparsed; do NOT treat
    #: it as the rent.
    max_term_rent: int | None = None
    currency: str = "USD"
    sqft: int | None = None
    #: Verbatim availability, e.g. "Now", "Sep 3". No year is rendered, so this
    #: is deliberately not converted to a date.
    available_text: str | None = None
    model_name: str | None = None
    photo_count: int = 0
    video_count: int = 0
    floorplan_count: int = 0
    virtual_tour_count: int = 0
    apply_now_url: str | None = None


class FloorPlan(_BaseModel):
    """A floor-plan model, grouping zero or more units."""

    name: str | None = None
    model_key: str | None = None
    rental_key: str | None = None
    beds: float | None = None
    baths: float | None = None
    price_text: str | None = None
    rent_min: int | None = None
    rent_max: int | None = None
    summary_text: str | None = None
    sqft_min: int | None = None
    sqft_max: int | None = None
    units: list[Unit] = Field(default_factory=list)
    #: 0 on properties whose layout lists plans without individual units — that
    #: is the site's own markup, not missing data.
    units_available: int = 0


class Property(_BaseModel):
    """An apartments.com property (a complex, not a single home)."""

    property_id: str | None = None
    url: str
    name: str | None = None
    address_line: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    neighborhood: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    phone: str | None = None
    rent_range_text: str | None = None
    rent_min: int | None = None
    rent_max: int | None = None
    beds_text: str | None = None
    description: str | None = None
    amenities: list[str] = Field(default_factory=list)
    office_hours: list[str] = Field(default_factory=list)
    photos: list[str] = Field(default_factory=list)
    floor_plans: list[FloorPlan] = Field(default_factory=list)
    #: Every unit across every floor plan, flattened.
    units: list[Unit] = Field(default_factory=list)
    total_units_available: int = 0


class SearchResult(_BaseModel):
    """One property card on a search-results page.

    A card is a summary carrying a rent/bed rollup, not per-unit inventory —
    call :meth:`ApartmentsClient.get_property` with ``url`` for units.
    """

    property_id: str | None = None
    url: str | None = None
    name: str | None = None
    address: str | None = None
    street_address: str | None = None
    country_code: str | None = None
    phone: str | None = None
    pricing: list[dict[str, str]] = Field(default_factory=list)
    rent_min: int | None = None
    beds_text: str | None = None
    amenities: list[str] = Field(default_factory=list)
    is_featured: bool = False


class SearchResponse(_BaseModel):
    """A page of search results (40 cards per page)."""

    location: str
    url: str
    page: int = 1
    total_pages: int | None = None
    total_results: int | None = None
    results_on_page: int = 0
    results: list[SearchResult] = Field(default_factory=list)
