"""Pydantic models for Vinted API responses.

This module contains all the data models used by the Vinted API client.
All models are immutable (frozen) and use strict validation for type safety.

Models are organized into:
- Nested models: VintedPrice, VintedPhoto, VintedUserSummary, VintedSellerSummary
- Core models: VintedItemSummary, VintedItemDetail, VintedUserProfile
- Reference models: VintedBrand, VintedColor, VintedStatus, VintedMarket
- Response envelopes: SearchResponse, ItemDetailResponse, etc.
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
        str_strip_whitespace=True,
    )


# =============================================================================
# Nested Models
# =============================================================================


class VintedPrice(_BaseModel):
    """Price information for a Vinted item.

    Attributes:
        amount: Price amount as a string (e.g. "12.50").
        currency_code: ISO currency code (e.g. "EUR").
    """

    amount: str
    currency_code: str


class VintedPhoto(_BaseModel):
    """A photo attached to a Vinted item.

    Attributes:
        id: Unique photo identifier.
        url: URL to the photo.
        dominant_color: Hex color code of the dominant color.
        is_main: Whether this is the main/primary photo.
        width: Photo width in pixels.
        height: Photo height in pixels.
        full_size_url: URL to the full-size photo.
    """

    id: int
    url: str
    dominant_color: str | None = None
    is_main: bool = False
    width: int | None = None
    height: int | None = None
    full_size_url: str | None = None


class VintedUserSummary(_BaseModel):
    """Summary of a Vinted user (as seen on item listings).

    Attributes:
        id: Unique user identifier.
        login: Username.
        photo_url: Profile photo URL.
        business: Whether the user is a business account.
    """

    id: int
    login: str
    photo_url: str | None = None
    business: bool = False


class VintedSellerSummary(_BaseModel):
    """Extended seller summary with reputation data.

    Attributes:
        id: Unique user identifier.
        login: Username.
        photo_url: Profile photo URL.
        business: Whether the user is a business account.
        feedback_count: Total number of feedback ratings.
        feedback_reputation: Reputation score (0.0 - 1.0).
        item_count: Number of items listed.
        location: Seller location string.
        last_seen: Last seen timestamp.
        badges: List of badge identifiers.
    """

    id: int
    login: str
    photo_url: str | None = None
    business: bool = False
    feedback_count: int | None = None
    feedback_reputation: float | None = None
    item_count: int | None = None
    location: str | None = None
    last_seen: str | None = None
    badges: list[str] = Field(default_factory=list)


# =============================================================================
# Core Models
# =============================================================================


class VintedItemSummary(_BaseModel):
    """Summary of a Vinted item (as seen in search results).

    Attributes:
        id: Unique item identifier.
        title: Item title.
        price: Item price.
        brand_title: Brand name.
        size_title: Size label.
        status: Item condition status.
        url: URL to the item page.
        favourite_count: Number of users who favourited this item.
        view_count: Number of views.
        user: Summary of the item owner.
        photo: Main photo.
        photos: All photos attached to the item.
        seller_country_code: Physical country of the seller as an upper-case
            ISO-2 code (e.g. "FR"), or None. Populated only when the
            ``seller_country`` search filter is used.
    """

    id: int
    title: str = ""
    price: VintedPrice | None = None
    brand_title: str | None = None
    size_title: str | None = None
    status: str | None = None
    url: str | None = None
    favourite_count: int = 0
    view_count: int = 0
    user: VintedUserSummary | None = None
    photo: VintedPhoto | None = None
    photos: list[VintedPhoto] = Field(default_factory=list)
    seller_country_code: str | None = None


class VintedItemDetail(_BaseModel):
    """Detailed information about a single Vinted item.

    Extends VintedItemSummary with additional fields available on the detail page.

    Attributes:
        id: Unique item identifier.
        title: Item title.
        price: Item price.
        brand_title: Brand name.
        size_title: Size label.
        status: Item condition status.
        url: URL to the item page.
        favourite_count: Number of users who favourited this item.
        view_count: Number of views.
        user: Summary of the item owner.
        photo: Main photo.
        photos: All photos attached to the item.
        description: Full item description.
        catalog_id: Catalog/category identifier.
        color1: Primary color name.
        seller: Extended seller information.
        category: Category name.
        upload_date: When the item was uploaded (ISO format).
        can_buy: Whether the item can be purchased.
        instant_buy: Whether instant buy is enabled.
        is_closed: Whether the listing is closed.
        is_reserved: Whether the item is reserved.
        is_hidden: Whether the item is hidden.
        size_id: Numeric size identifier.
        status_id: Numeric status identifier.
        brand_id: Numeric brand identifier.
    """

    id: int
    title: str = ""
    price: VintedPrice | None = None
    brand_title: str | None = None
    size_title: str | None = None
    status: str | None = None
    url: str | None = None
    favourite_count: int = 0
    view_count: int = 0
    user: VintedUserSummary | None = None
    photo: VintedPhoto | None = None
    photos: list[VintedPhoto] = Field(default_factory=list)

    # Detail-only fields
    description: str | None = None
    catalog_id: int | None = None
    color1: str | None = None
    seller: VintedSellerSummary | None = None
    category: list[str] | str | None = None
    upload_date: str | None = None
    can_buy: bool | None = None
    instant_buy: bool | None = None
    is_closed: bool | None = None
    is_reserved: bool | None = None
    is_hidden: bool | None = None
    size_id: int | None = None
    status_id: int | None = None
    brand_id: int | None = None


class VintedUserProfile(_BaseModel):
    """Full Vinted user profile.

    Attributes:
        id: Unique user identifier.
        login: Username.
        photo_url: Profile photo URL.
        business: Whether the user is a business account.
        country_code: ISO country code.
        city: City name.
        feedback_count: Total number of feedback ratings.
        feedback_reputation: Reputation score (0.0 - 1.0).
        positive_feedback_count: Number of positive ratings.
        neutral_feedback_count: Number of neutral ratings.
        negative_feedback_count: Number of negative ratings.
        item_count: Number of items listed.
        followers_count: Number of followers.
        following_count: Number of users being followed.
        is_online: Whether the user is currently online.
        is_on_holiday: Whether holiday mode is enabled.
        last_loged_on_ts: Last login timestamp.
        profile_url: URL to the user profile page.
        locale: User locale (e.g. "fr").
    """

    id: int
    login: str
    photo_url: str | None = None
    business: bool = False
    country_code: str | None = None
    city: str | None = None
    feedback_count: int | None = None
    feedback_reputation: float | None = None
    positive_feedback_count: int | None = None
    neutral_feedback_count: int | None = None
    negative_feedback_count: int | None = None
    item_count: int | None = None
    followers_count: int | None = None
    following_count: int | None = None
    is_online: bool | None = None
    is_on_holiday: bool | None = None
    last_loged_on_ts: str | None = None
    profile_url: str | None = None
    locale: str | None = None


# =============================================================================
# Reference Models
# =============================================================================


class VintedBrand(_BaseModel):
    """A Vinted brand.

    Attributes:
        id: Unique brand identifier.
        title: Brand name.
        slug: URL-friendly brand slug.
        item_count: Number of items listed with this brand.
        favourite_count: Number of users who favourited this brand.
        is_luxury: Whether this is a luxury brand.
        url: URL to the brand page.
    """

    id: int
    title: str = ""
    slug: str | None = None
    item_count: int | None = None
    favourite_count: int | None = None
    is_luxury: bool | None = None
    url: str | None = None


class VintedColor(_BaseModel):
    """A Vinted color option.

    Attributes:
        id: Unique color identifier.
        title: Color name.
        hex: Hex color code.
        code: Internal color code.
    """

    id: int
    title: str = ""
    hex: str | None = None
    code: str | None = None


class VintedStatus(_BaseModel):
    """A Vinted item condition status.

    Attributes:
        id: Unique status identifier.
        title: Status label (e.g. "New with tags", "Good").
    """

    id: int
    title: str = ""


class VintedMarket(_BaseModel):
    """A Vinted market (country/region).

    Attributes:
        code: Market code (e.g. "fr", "de").
        domain: Market domain (e.g. "vinted.fr").
        country: Country name.
        currency: Currency code (e.g. "EUR").
        name: Market display name.
    """

    code: str
    domain: str | None = None
    country: str | None = None
    currency: str | None = None
    name: str | None = None


# =============================================================================
# Pagination
# =============================================================================


class VintedPagination(_BaseModel):
    """Pagination metadata for Vinted responses.

    Attributes:
        current_page: Current page number.
        total_pages: Total number of pages.
        total_entries: Total number of entries across all pages.
        per_page: Number of entries per page.
    """

    current_page: int = 1
    total_pages: int = 1
    total_entries: int = 0
    per_page: int = 20


# =============================================================================
# Response Envelopes
# =============================================================================


class SearchResponse(_BaseModel):
    """Response from the Vinted search endpoint.

    Attributes:
        items: List of matching items.
        pagination: Pagination metadata.
        market: Market code used for the search.
        seller_country: Echo of the normalized ``seller_country`` filter applied
            to this search (comma-separated ISO-2 codes, e.g. "fr,be"), or None
            when no filter was used.
    """

    items: list[VintedItemSummary] = Field(default_factory=list)
    pagination: VintedPagination | None = None
    market: str = ""
    seller_country: str | None = None


class ItemDetailResponse(_BaseModel):
    """Response from the Vinted item detail endpoint.

    Attributes:
        item: The detailed item data.
        market: Market code used for the request.
    """

    item: VintedItemDetail | None = None
    market: str = ""


class UserProfileResponse(_BaseModel):
    """Response from the Vinted user profile endpoint.

    Attributes:
        user: The user profile data.
        market: Market code used for the request.
    """

    user: VintedUserProfile | None = None
    market: str = ""


class UserItemsResponse(_BaseModel):
    """Response from the Vinted user items endpoint.

    Attributes:
        items: List of the user's items.
        pagination: Pagination metadata.
        market: Market code used for the request.
    """

    items: list[VintedItemSummary] = Field(default_factory=list)
    pagination: VintedPagination | None = None
    market: str = ""


class BrandsResponse(_BaseModel):
    """Response from the Vinted brands endpoint.

    Attributes:
        brands: List of matching brands.
        pagination: Pagination metadata (may be absent for small results).
    """

    brands: list[VintedBrand] = Field(default_factory=list)
    pagination: VintedPagination | None = None


class ColorsResponse(_BaseModel):
    """Response from the Vinted colors endpoint.

    Attributes:
        colors: List of available colors.
    """

    colors: list[VintedColor] = Field(default_factory=list)


class StatusesResponse(_BaseModel):
    """Response from the Vinted statuses endpoint.

    Attributes:
        statuses: List of available item condition statuses.
    """

    statuses: list[VintedStatus] = Field(default_factory=list)


class MarketsResponse(_BaseModel):
    """Response from the Vinted markets endpoint.

    Attributes:
        markets: List of available Vinted markets.
    """

    markets: list[VintedMarket] = Field(default_factory=list)
