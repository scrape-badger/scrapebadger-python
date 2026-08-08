"""Pydantic models for Bing API responses.

These models mirror the backend ``bing_scraper`` response schema
field-for-field. All models are immutable (frozen) and ignore unknown fields
for forward compatibility.
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
# Web search
# =============================================================================


class DeepLink(_BaseModel):
    """A sitelink shown under an organic result."""

    title: str
    url: str | None = None


class OrganicResult(_BaseModel):
    """One organic result from a Bing web SERP."""

    position: int
    title: str
    url: str | None = None
    display_url: str | None = None
    site_name: str | None = None
    snippet: str | None = None
    deep_links: list[DeepLink] = Field(default_factory=list)


class Ad(_BaseModel):
    """A sponsored result on the SERP."""

    position: int
    title: str
    url: str | None = None
    display_url: str | None = None
    snippet: str | None = None


class SearchResponse(_BaseModel):
    """A page of Bing web search results."""

    query: str
    market: str
    total_results: int | None = None
    total_results_text: str | None = None
    result_count: int = 0
    results: list[OrganicResult] = Field(default_factory=list)
    ads: list[Ad] = Field(default_factory=list)
    related_searches: list[str] = Field(default_factory=list)


# =============================================================================
# Images
# =============================================================================


class ImageResult(_BaseModel):
    """One image from Bing image search."""

    position: int
    title: str | None = None
    image_url: str | None = None
    thumbnail_url: str | None = None
    source_url: str | None = None
    source_domain: str | None = None
    width: int | None = None
    height: int | None = None


class ImagesResponse(_BaseModel):
    """Response from the Bing image search endpoint."""

    query: str
    market: str
    result_count: int = 0
    results: list[ImageResult] = Field(default_factory=list)


# =============================================================================
# Videos
# =============================================================================


class VideoResult(_BaseModel):
    """One video from Bing video search."""

    position: int
    title: str | None = None
    url: str | None = None
    thumbnail_url: str | None = None
    duration: str | None = None
    source: str | None = None
    publisher: str | None = None
    views: str | None = None
    published: str | None = None


class VideosResponse(_BaseModel):
    """Response from the Bing video search endpoint."""

    query: str
    market: str
    result_count: int = 0
    results: list[VideoResult] = Field(default_factory=list)


# =============================================================================
# News
# =============================================================================


class NewsArticle(_BaseModel):
    """One article from the Bing news vertical."""

    position: int
    title: str | None = None
    url: str | None = None
    source: str | None = None
    snippet: str | None = None
    published: str | None = None
    published_at: str | None = None
    published_utc: float | None = None


class NewsResponse(_BaseModel):
    """Response from the Bing news endpoint."""

    query: str
    market: str
    result_count: int = 0
    results: list[NewsArticle] = Field(default_factory=list)


# =============================================================================
# Autocomplete
# =============================================================================


class AutocompleteResponse(_BaseModel):
    """Search-box suggestions for a partial term."""

    query: str
    market: str
    result_count: int = 0
    suggestions: list[str] = Field(default_factory=list)


# =============================================================================
# Reference
# =============================================================================


class Market(_BaseModel):
    """A supported Bing market."""

    code: str
    name: str
    country: str


class MarketsResponse(_BaseModel):
    """All supported Bing markets."""

    result_count: int = 0
    markets: list[Market] = Field(default_factory=list)
