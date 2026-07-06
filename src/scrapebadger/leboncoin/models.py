"""Pydantic models for Leboncoin API responses.

These models mirror the backend ``leboncoin_scraper`` response schema
field-for-field. All models are immutable (frozen) and ignore unknown fields
for forward compatibility. Every datetime field ships in BOTH the raw
Leboncoin form (``*_date``) and an ISO-8601 UTC string (``*_at``).
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
# Shared / nested models
# =============================================================================


class Attribute(_BaseModel):
    """A category-specific spec (vehicle mileage, real-estate DPE, etc.)."""

    key: str
    key_label: str | None = None
    value: str | None = None
    value_label: str | None = None
    values: list[str] = Field(default_factory=list)
    values_label: list[str] = Field(default_factory=list)
    generic: bool | None = None


class Location(_BaseModel):
    """A geographic location (region/department/city/coordinates)."""

    country_id: str | None = None
    region_id: str | None = None
    region_name: str | None = None
    department_id: str | None = None
    department_name: str | None = None
    city: str | None = None
    city_label: str | None = None
    zipcode: str | None = None
    district: str | None = None
    lat: float | None = None
    lng: float | None = None
    source: str | None = None
    provider: str | None = None
    is_shape: bool | None = None


class Owner(_BaseModel):
    """Seller stub embedded in each ad."""

    user_id: str | None = None
    store_id: str | None = None
    type: str | None = None  # "private" | "pro"
    name: str | None = None
    siren: str | None = None
    no_salesmen: bool | None = None
    activity_sector: str | None = None
    online_store_id: str | None = None


class Images(_BaseModel):
    """The image gallery of an ad."""

    nb_images: int = 0
    thumb_url: str | None = None
    small_url: str | None = None
    urls: list[str] = Field(default_factory=list)
    urls_thumb: list[str] = Field(default_factory=list)
    urls_large: list[str] = Field(default_factory=list)


# =============================================================================
# Ad (search summary + detail share this shape)
# =============================================================================


class Ad(_BaseModel):
    """A Leboncoin classified ad (search summary + detail share this shape)."""

    list_id: int
    subject: str = ""
    body: str | None = None
    brand: str | None = None
    ad_type: str | None = None  # "offer" | "demand"
    url: str | None = None
    status: str | None = None

    category_id: str | None = None
    category_name: str | None = None

    price: list[int] = Field(default_factory=list)
    price_cents: int | None = None
    price_eur: float | None = None
    currency: str = "EUR"

    # Dates — raw + ISO
    first_publication_date: str | None = None
    first_publication_at: str | None = None
    index_date: str | None = None
    index_at: str | None = None
    expiration_date: str | None = None
    expiration_at: str | None = None

    has_phone: bool | None = None
    favorites: int | None = None

    images: Images = Field(default_factory=Images)
    attributes: list[Attribute] = Field(default_factory=list)
    location: Location = Field(default_factory=Location)
    owner: Owner = Field(default_factory=Owner)

    # Ad options / boosts (present in web payload)
    options: dict[str, Any] = Field(default_factory=dict)


# =============================================================================
# Seller / store
# =============================================================================


class FeedbackScores(_BaseModel):
    """Aggregate buyer feedback scores for a seller."""

    overall_score: float | None = None
    received_count: int | None = None
    category_scores: dict[str, Any] = Field(default_factory=dict)


class StoreRatingReview(_BaseModel):
    """A single store rating review (pro stores)."""

    author_name: str | None = None
    rating_value: float | None = None
    text: str | None = None
    review_time: str | None = None


class Seller(_BaseModel):
    """A Leboncoin seller's public profile (/sellers/{user_id})."""

    user_id: str
    store_id: str | None = None
    online_store_id: str | None = None
    name: str | None = None
    account_type: str | None = None  # "private" | "pro"
    registered_at: str | None = None
    total_ads: int | None = None
    description: str | None = None
    profile_picture_url: str | None = None
    location: Location = Field(default_factory=Location)
    badges: list[dict[str, Any]] = Field(default_factory=list)
    feedback: FeedbackScores | None = None
    reply_rate: float | None = None
    reply_time_text: str | None = None
    presence_status: str | None = None
    last_activity: str | None = None

    # Pro store extras (present only when account_type == "pro")
    siren: str | None = None
    siret: str | None = None
    activity_sector: str | None = None
    website_url: str | None = None
    opening_hours: dict[str, Any] | list[Any] | None = None
    store_rating_value: float | None = None
    store_ratings_total: int | None = None
    store_reviews: list[StoreRatingReview] = Field(default_factory=list)


# =============================================================================
# Reference
# =============================================================================


class Category(_BaseModel):
    """A reference category alias (for /categories)."""

    category_id: str
    key: str
    label: str
    parent_id: str | None = None


class Region(_BaseModel):
    """A reference region (for /regions)."""

    region_id: str
    key: str
    name: str


class Department(_BaseModel):
    """A reference department (for /departments)."""

    department_id: str
    region_id: str
    name: str


class LocationSuggestion(_BaseModel):
    """A single location autocomplete suggestion (for /locations/search)."""

    label: str
    location_type: str | None = None
    region_id: str | None = None
    department_id: str | None = None
    city: str | None = None
    zipcode: str | None = None
    lat: float | None = None
    lng: float | None = None


# =============================================================================
# Response envelopes
# =============================================================================


class SearchResponse(_BaseModel):
    """Response for /search."""

    ads: list[Ad] = Field(default_factory=list)
    total: int | None = None
    total_all: int | None = None
    total_pro: int | None = None
    total_private: int | None = None
    total_shippable: int | None = None
    max_pages: int | None = None
    page: int = 1
    limit: int = 35
    source: str = "api"  # "api" (finder) or "web" (rendered __NEXT_DATA__)


class AdResponse(_BaseModel):
    """Response for /ads/{list_id}."""

    ad: Ad


class SimilarResponse(_BaseModel):
    """Response for /ads/{list_id}/similar."""

    list_id: int
    ads: list[Ad] = Field(default_factory=list)


class SellerResponse(_BaseModel):
    """Response for /sellers/{user_id}."""

    seller: Seller


class SellerListingsResponse(_BaseModel):
    """Response for /sellers/{user_id}/listings."""

    user_id: str
    ads: list[Ad] = Field(default_factory=list)
    total: int | None = None
    page: int = 1
    limit: int = 35


class CategoriesResponse(_BaseModel):
    """Response for /categories."""

    categories: list[Category] = Field(default_factory=list)


class RegionsResponse(_BaseModel):
    """Response for /regions."""

    regions: list[Region] = Field(default_factory=list)


class DepartmentsResponse(_BaseModel):
    """Response for /departments."""

    departments: list[Department] = Field(default_factory=list)


class LocationSearchResponse(_BaseModel):
    """Response for /locations/search."""

    query: str
    suggestions: list[LocationSuggestion] = Field(default_factory=list)


class MarketsResponse(_BaseModel):
    """Response for /markets."""

    markets: list[dict[str, Any]] = Field(default_factory=list)
