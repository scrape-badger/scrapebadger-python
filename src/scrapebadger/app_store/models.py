"""Pydantic models for Apple App Store API responses.

These models mirror the backend ``app_store_scraper`` response schema
field-for-field. All models are immutable (frozen) and ignore unknown fields
for forward compatibility.

Two upstream sources feed these models, and the split matters for reliability:

* **iTunes** — the documented public API. Every field on ``App``, ``Review``,
  ``ChartEntry`` and ``Developer`` comes from here.
* **Storefront** — the server-rendered product page, whose embedded JSON
  carries what the API omits: the 1-5 star histogram, the in-app-purchase
  price list, per-device screenshots at full resolution, chart position,
  Editors' Choice, and the App Privacy breakdown. Everything sourced from it
  lives under ``App.extras`` and is OPTIONAL — a detail response degrades to
  iTunes-only rather than failing.

Every datetime ships in BOTH forms: ``*_utc`` (Unix seconds, for maths and
sorting) and ``*_at`` (ISO 8601 UTC string, for humans).
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
# Storefront-only value objects (App.extras)
# =============================================================================


class Screenshot(_BaseModel):
    """A screenshot at its native resolution.

    iTunes returns screenshots pre-scaled to a fixed thumbnail size; the
    storefront returns the source artwork plus its true dimensions, so these
    are the full-resolution originals.
    """

    url: str
    width: int | None = None
    height: int | None = None


class InAppPurchase(_BaseModel):
    """One IAP tier as displayed on the product page.

    Apple exposes only the display price (localised, tax-inclusive per
    storefront) — there is no numeric/currency split on the page.
    """

    name: str
    price: str | None = None


class RatingHistogram(_BaseModel):
    """Star breakdown behind the average rating.

    ``total`` is Apple's own count for the storefront and can differ slightly
    from the iTunes ``rating_count`` — the two are computed on different
    schedules. Both are surfaced rather than reconciled.
    """

    average: float | None = None
    total: int | None = None
    one_star: int = 0
    two_star: int = 0
    three_star: int = 0
    four_star: int = 0
    five_star: int = 0


class PrivacyType(_BaseModel):
    """One App Privacy ("nutrition label") group and its data categories."""

    identifier: str | None = None
    title: str | None = None
    detail: str | None = None
    categories: list[str] = Field(default_factory=list)


class AppExtras(_BaseModel):
    """Storefront-sourced enrichment. Absent when the page fetch/parse fails."""

    rating_histogram: RatingHistogram | None = None
    has_in_app_purchases: bool | None = None
    in_app_purchases: list[InAppPurchase] = Field(default_factory=list)
    iphone_screenshots: list[Screenshot] = Field(default_factory=list)
    ipad_screenshots: list[Screenshot] = Field(default_factory=list)
    whats_new: str | None = None
    whats_new_version: str | None = None
    description: str | None = None
    chart_position: int | None = None
    chart_category: str | None = None
    is_editors_choice: bool = False
    privacy_types: list[PrivacyType] = Field(default_factory=list)
    # Raw "Information" rows (Seller / Size / Category / Compatibility /
    # Languages / Age Rating / Copyright …) as the page displays them. A flat
    # dict because Apple adds and renames rows per app type.
    information: dict[str, str] = Field(default_factory=dict)


# =============================================================================
# App
# =============================================================================


class App(_BaseModel):
    """An app, as returned by iTunes search and lookup (identical shapes)."""

    # Identity
    app_id: int | None = None
    bundle_id: str | None = None
    name: str | None = None
    censored_name: str | None = None
    kind: str | None = None
    url: str | None = None

    # Developer
    developer_id: int | None = None
    developer_name: str | None = None
    developer_url: str | None = None
    seller_name: str | None = None
    seller_url: str | None = None

    # Pricing
    price: float | None = None
    currency: str | None = None
    formatted_price: str | None = None

    # Ratings
    rating: float | None = None
    rating_count: int | None = None
    rating_current_version: float | None = None
    rating_count_current_version: int | None = None

    # Content
    description: str | None = None
    release_notes: str | None = None
    version: str | None = None
    minimum_os_version: str | None = None
    file_size_bytes: int | None = None
    content_rating: str | None = None
    advisories: list[str] = Field(default_factory=list)
    genres: list[str] = Field(default_factory=list)
    genre_ids: list[int] = Field(default_factory=list)
    primary_genre: str | None = None
    primary_genre_id: int | None = None
    language_codes: list[str] = Field(default_factory=list)
    supported_devices: list[str] = Field(default_factory=list)
    features: list[str] = Field(default_factory=list)
    is_game_center_enabled: bool | None = None
    is_vpp_device_based_licensing_enabled: bool | None = None

    # Artwork
    icon_url: str | None = None
    icon_url_60: str | None = None
    icon_url_100: str | None = None
    screenshot_urls: list[str] = Field(default_factory=list)
    ipad_screenshot_urls: list[str] = Field(default_factory=list)
    appletv_screenshot_urls: list[str] = Field(default_factory=list)

    # Dates (dual form)
    release_date_utc: float | None = None
    release_date_at: str | None = None
    current_version_release_date_utc: float | None = None
    current_version_release_date_at: str | None = None

    # Storefront enrichment (detail endpoint only)
    extras: AppExtras | None = None


class SearchResponse(_BaseModel):
    """Full-text search results across one App Store catalogue."""

    query: str
    country: str
    entity: str
    result_count: int
    apps: list[App] = Field(default_factory=list)


# =============================================================================
# Reviews
# =============================================================================


class Review(_BaseModel):
    """One customer review."""

    review_id: str | None = None
    user_name: str | None = None
    user_url: str | None = None
    title: str | None = None
    content: str | None = None
    rating: int | None = None
    version: str | None = None
    vote_sum: int | None = None
    vote_count: int | None = None
    updated_utc: float | None = None
    updated_at: str | None = None


class ReviewsResponse(_BaseModel):
    """A page of customer reviews — 50 per page, pages 1-10."""

    app_id: str
    country: str
    page: int
    sort: str
    result_count: int
    reviews: list[Review] = Field(default_factory=list)


# =============================================================================
# Charts
# =============================================================================


class ChartEntry(_BaseModel):
    """One app in a top chart. ``rank`` is its position in Apple's feed."""

    rank: int
    app_id: int | None = None
    name: str | None = None
    url: str | None = None
    developer_name: str | None = None
    developer_url: str | None = None
    icon_url: str | None = None
    price: float | None = None
    currency: str | None = None
    formatted_price: str | None = None
    genre: str | None = None
    genre_id: int | None = None
    summary: str | None = None
    rights: str | None = None
    release_date_utc: float | None = None
    release_date_at: str | None = None


class ChartsResponse(_BaseModel):
    """A top chart for one storefront, optionally scoped to one genre."""

    country: str
    type: str
    entity: str
    genre_id: int | None = None
    result_count: int
    apps: list[ChartEntry] = Field(default_factory=list)


# =============================================================================
# Developer
# =============================================================================


class Developer(_BaseModel):
    """An App Store developer (Apple's ``artist`` entry)."""

    developer_id: int | None = None
    name: str | None = None
    developer_type: str | None = None
    url: str | None = None


class DeveloperResponse(_BaseModel):
    """A developer and every app they publish in the storefront."""

    country: str
    developer: Developer | None = None
    result_count: int
    apps: list[App] = Field(default_factory=list)


# =============================================================================
# Reference
# =============================================================================


class Genre(_BaseModel):
    """An App Store genre, for use with ``charts(genre=...)``."""

    genre_id: int
    name: str
    parent_id: int | None = None


class GenresResponse(_BaseModel):
    """Every chartable App Store genre id."""

    result_count: int
    genres: list[Genre] = Field(default_factory=list)


class Market(_BaseModel):
    """A supported App Store storefront."""

    code: str
    name: str


class MarketsResponse(_BaseModel):
    """Supported App Store storefronts.

    Informational: the endpoints accept any well-formed 2-letter code and let
    Apple arbitrate, so a storefront missing from this list still works.
    """

    result_count: int
    markets: list[Market] = Field(default_factory=list)
