"""Pydantic models for Google Play Store API responses.

These models mirror the backend ``google_play_scraper`` response schema
field-for-field. All models are immutable (frozen) and ignore unknown fields
for forward compatibility.

Play is one global host localised by two independent parameters: ``country``
(``gl`` — pricing, availability, chart ranking) and ``lang`` (``hl`` — the
language of descriptions and reviews).

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
# Shared value objects
# =============================================================================


class Price(_BaseModel):
    """An app's purchase price. Free apps report 0.0 with ``is_free=True``."""

    price: float | None = None
    currency: str | None = None
    price_text: str | None = None
    is_free: bool | None = None


class Developer(_BaseModel):
    """The publisher, plus the legal entity Play discloses beneath it.

    ``name`` and ``legal_name`` differ more often than not (WhatsApp LLC vs
    Meta Platforms, Inc.), and only the legal block carries the postal address
    and phone number.
    """

    name: str | None = None
    developer_id: str | None = None
    url: str | None = None
    email: str | None = None
    website: str | None = None
    address: str | None = None
    phone: str | None = None
    legal_name: str | None = None
    legal_email: str | None = None


class RatingHistogram(_BaseModel):
    """The 1-5 star breakdown Play renders as the bar chart."""

    one_star: int | None = None
    two_star: int | None = None
    three_star: int | None = None
    four_star: int | None = None
    five_star: int | None = None


class Category(_BaseModel):
    """A Play app or game category."""

    name: str | None = None
    category_id: str | None = None
    url: str | None = None


class ChartRank(_BaseModel):
    """The "#1 top free communication" badge, when the app carries one."""

    rank: str | None = None
    chart: str | None = None


class DataSafetySection(_BaseModel):
    """One row of Play's Data Safety card.

    A row is a headline plus an optional blurb. The detail page carries only
    this summary; the per-data-type breakdown lives behind Play's separate
    "See details" screen and is not available.
    """

    title: str | None = None
    description: str | None = None


class PermissionGroup(_BaseModel):
    """An Android permission group and the individual permissions inside it."""

    group: str | None = None
    icon_url: str | None = None
    permissions: list[str] = Field(default_factory=list)


# =============================================================================
# Apps
# =============================================================================


class AppCard(_BaseModel):
    """An app as it appears in a list (search, developer, cluster, similar).

    Play's list card is a genuinely rich record — it carries the description,
    installs, rating and price, so a search result rarely needs a follow-up
    detail fetch just to rank or filter.
    """

    app_id: str
    title: str | None = None
    developer: str | None = None
    summary: str | None = None
    description: str | None = None
    icon: str | None = None
    header_image: str | None = None
    screenshots: list[str] = Field(default_factory=list)
    score: float | None = None
    score_text: str | None = None
    installs: str | None = None
    genre: str | None = None
    content_rating: str | None = None
    price: Price | None = None
    url: str | None = None


class App(_BaseModel):
    """Full app detail from ``/store/apps/details``."""

    app_id: str
    title: str | None = None
    url: str | None = None
    description: str | None = None
    summary: str | None = None
    developer: Developer | None = None

    # Ratings
    score: float | None = None
    score_text: str | None = None
    ratings: int | None = None
    reviews: int | None = None
    histogram: RatingHistogram | None = None

    # Reach
    installs: str | None = None
    installs_short: str | None = None
    min_installs: int | None = None
    max_installs: int | None = None
    chart_rank: ChartRank | None = None

    # Commercials
    price: Price | None = None
    offers_iap: bool | None = None
    iap_range: str | None = None
    contains_ads: bool | None = None
    ad_supported: bool | None = None

    # Classification
    genre: str | None = None
    genre_id: str | None = None
    genre_url: str | None = None
    content_rating: str | None = None
    content_rating_description: str | None = None

    # Media
    icon: str | None = None
    header_image: str | None = None
    screenshots: list[str] = Field(default_factory=list)
    video: str | None = None
    video_image: str | None = None

    # Release / build
    released: str | None = None
    released_utc: float | None = None
    released_at: str | None = None
    updated_utc: float | None = None
    updated_at: str | None = None
    version: str | None = None
    android_version: str | None = None
    android_version_text: str | None = None
    recent_changes: str | None = None

    # Compliance
    privacy_policy: str | None = None
    data_safety: list[DataSafetySection] = Field(default_factory=list)
    permissions: list[PermissionGroup] = Field(default_factory=list)

    # Discovery
    similar_apps_url: str | None = None
    similar_apps: list[AppCard] = Field(default_factory=list)


# =============================================================================
# Reviews
# =============================================================================


class Review(_BaseModel):
    """One user review, with the developer's reply where one exists."""

    review_id: str | None = None
    user_name: str | None = None
    user_image: str | None = None
    score: int | None = None
    text: str | None = None
    thumbs_up: int | None = None
    review_created_version: str | None = None
    at_utc: float | None = None
    at: str | None = None
    reply_author: str | None = None
    reply_content: str | None = None
    replied_utc: float | None = None
    replied_at: str | None = None


class ReviewsResponse(_BaseModel):
    """A page of reviews. Play paginates by token only — there is no page number."""

    app_id: str
    sort: str
    result_count: int
    next_page_token: str | None = None
    reviews: list[Review] = Field(default_factory=list)


class PermissionsResponse(_BaseModel):
    """Every Android permission an app declares, grouped as Play groups them."""

    app_id: str
    result_count: int
    permission_groups: list[PermissionGroup] = Field(default_factory=list)


# =============================================================================
# Lists
# =============================================================================


class AppListResponse(_BaseModel):
    """Shared shape for every list endpoint — search, developer, similar, chart.

    One response model rather than four near-identical ones: the endpoints
    differ in how the URL is built, not in what comes back.
    """

    query: str | None = None
    url: str | None = None
    result_count: int
    apps: list[AppCard] = Field(default_factory=list)


# =============================================================================
# Reference
# =============================================================================


class CategoriesResponse(_BaseModel):
    """Every Play app and game category id."""

    result_count: int
    categories: list[Category] = Field(default_factory=list)


class Market(_BaseModel):
    """A supported storefront country (``gl``) or content language (``hl``)."""

    code: str
    name: str


class MarketsResponse(_BaseModel):
    """Supported storefront countries and content languages.

    ``markets`` and ``languages`` are independent: ``gl`` selects pricing,
    availability and chart ranking, ``hl`` selects the language of descriptions
    and reviews.
    """

    result_count: int
    markets: list[Market] = Field(default_factory=list)
    languages: list[Market] = Field(default_factory=list)
