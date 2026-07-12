"""Pydantic models for Depop API responses.

These models mirror the backend ``depop_scraper`` response schema
field-for-field. All models are immutable (frozen) and ignore unknown fields
for forward compatibility.

Depop is a single global host (depop.com) localised by ``market`` — the market
code selects the country and currency the storefront renders in. Search and
user-products endpoints return card grids; product and shop endpoints return
full detail.
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
# Search / user-products cards
# =============================================================================


class DepopCard(_BaseModel):
    """One Depop product card from a search or user-products grid."""

    slug: str
    url: str
    seller_username: str | None = None
    brand: str | None = None
    size: str | None = None
    price: str | None = None
    original_price: str | None = None
    currency: str | None = None
    is_sold: bool = False
    image: str | None = None


class SearchMeta(_BaseModel):
    """Pagination metadata for a card grid."""

    result_count: int = 0
    page: int = 1
    has_more: bool = False


class SearchResponse(_BaseModel):
    products: list[DepopCard] = Field(default_factory=list)
    meta: SearchMeta
    market: str
    query: str


# =============================================================================
# Product detail
# =============================================================================


class ProductDetail(_BaseModel):
    """Full Depop product detail."""

    id: int | None = None
    slug: str
    title: str | None
    description: str | None
    brand: str | None
    condition: str | None
    price: str | None
    currency: str | None
    availability: str | None
    seller_username: str | None
    images: list[str] = Field(default_factory=list)
    url: str


# =============================================================================
# Shop / user profile
# =============================================================================


class ShopProfile(_BaseModel):
    """A Depop seller's shop profile."""

    username: str
    name: str | None
    description: str | None
    rating_value: str | None
    rating_count: int | None
    follower_count: int | None
    url: str


class UserProductsResponse(_BaseModel):
    username: str
    products: list[DepopCard] = Field(default_factory=list)
    meta: SearchMeta
    market: str


# =============================================================================
# Markets
# =============================================================================


class Market(_BaseModel):
    """A supported Depop market (country + currency)."""

    code: str
    country_code: str
    currency: str
    name: str


class MarketsResponse(_BaseModel):
    markets: list[Market] = Field(default_factory=list)
