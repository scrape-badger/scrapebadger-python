"""Pydantic models for Yandex API responses.

These models mirror the backend ``yandex_scraper`` response schema
field-for-field. All models are immutable (frozen) and ignore unknown fields
for forward compatibility.
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
# Web search
# =============================================================================


class Sitelink(_BaseModel):
    """One sitelink nested under an organic result or ad."""

    title: str | None = None
    url: str | None = None
    snippet: str | None = None


class OrganicResult(_BaseModel):
    """One organic web result (ads share the same shape)."""

    position: int | None = None
    title: str | None = None
    url: str | None = None
    displayed_url: str | None = None
    domain: str | None = None
    snippet: str | None = None
    sitelinks: list[Sitelink] = Field(default_factory=list)


class Pagination(_BaseModel):
    """SERP pagination block."""

    current: int | None = None
    next_url: str | None = None
    other_pages: list[dict[str, Any]] = Field(default_factory=list)


class SearchResponse(_BaseModel):
    """A page of Yandex web results."""

    query: str | None = None
    domain: str | None = None
    page: int | None = None
    result_count: int | None = None
    organic_results: list[OrganicResult] = Field(default_factory=list)
    ads: list[OrganicResult] = Field(default_factory=list)
    inline_images: list[dict[str, Any]] = Field(default_factory=list)
    inline_videos: list[dict[str, Any]] = Field(default_factory=list)
    related_searches: list[str] = Field(default_factory=list)
    pagination: Pagination | None = None


# =============================================================================
# Image search
# =============================================================================


class Image(_BaseModel):
    """An image reference with dimensions."""

    url: str | None = None
    width: int | None = None
    height: int | None = None


class ImageResult(_BaseModel):
    """One image-search result."""

    position: int | None = None
    title: str | None = None
    source: str | None = None
    source_url: str | None = None
    thumbnail: str | None = None
    image: Image | None = None
    snippet: str | None = None


class ImagesResponse(_BaseModel):
    """A page of image-search results."""

    query: str | None = None
    domain: str | None = None
    page: int | None = None
    result_count: int | None = None
    results: list[ImageResult] = Field(default_factory=list)
    suggested_searches: list[str] = Field(default_factory=list)


# =============================================================================
# Reverse image search
# =============================================================================


class ReverseSite(_BaseModel):
    """One page where the query image (or a variant) was found."""

    title: str | None = None
    description: str | None = None
    url: str | None = None
    domain: str | None = None
    thumbnail: Image | None = None
    original_image: Image | None = None


class SimilarImage(_BaseModel):
    """One visually-similar image."""

    title: str | None = None
    thumbnail: str | None = None
    url: str | None = None
    width: int | None = None
    height: int | None = None


class Tag(_BaseModel):
    """A CBIR tag / suggested refinement."""

    text: str | None = None
    url: str | None = None


class OtherSize(_BaseModel):
    """The same image at another resolution."""

    label: str | None = None
    url: str | None = None
    width: int | None = None
    height: int | None = None


class ReverseImageResponse(_BaseModel):
    """The Yandex reverse-image (CBIR) response."""

    query_image_url: str | None = None
    domain: str | None = None
    cbir_id: str | None = None
    is_empty: bool | None = None
    result_count: int | None = None
    sites: list[ReverseSite] = Field(default_factory=list)
    similar_images: list[SimilarImage] = Field(default_factory=list)
    tags: list[Tag] = Field(default_factory=list)
    other_sizes: list[OtherSize] = Field(default_factory=list)


# =============================================================================
# Markets (reference)
# =============================================================================


class Market(_BaseModel):
    """A supported Yandex market."""

    code: str | None = None
    name: str | None = None
    domain: str | None = None
    country_code: str | None = None
    default_lr: int | None = None
    lang: str | None = None


class MarketsResponse(_BaseModel):
    """All supported Yandex markets."""

    result_count: int | None = None
    markets: list[Market] = Field(default_factory=list)
