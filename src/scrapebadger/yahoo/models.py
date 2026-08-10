"""Pydantic models for Yahoo API responses.

These models mirror the backend ``yahoo_scraper`` response schema
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


class OrganicResult(_BaseModel):
    """One organic result from a Yahoo web SERP."""

    position: int
    title: str
    url: str | None = None
    display_url: str | None = None
    snippet: str | None = None


class Ad(_BaseModel):
    """A sponsored result on the SERP."""

    position: int
    title: str
    url: str | None = None
    display_url: str | None = None
    snippet: str | None = None


class SearchResponse(_BaseModel):
    """A page of Yahoo web search results.

    Yahoo does not expose a total-results count on the web SERP, so only
    ``result_count`` (results in this response) is available.
    """

    query: str
    market: str
    result_count: int = 0
    results: list[OrganicResult] = Field(default_factory=list)
    ads: list[Ad] = Field(default_factory=list)
    related_searches: list[str] = Field(default_factory=list)


# =============================================================================
# Images
# =============================================================================


class ImageResult(_BaseModel):
    """One image from Yahoo image search."""

    position: int
    title: str | None = None
    image_url: str | None = None
    thumbnail_url: str | None = None
    source_url: str | None = None
    source_domain: str | None = None
    width: int | None = None
    height: int | None = None


class ImagesResponse(_BaseModel):
    """Response from the Yahoo image search endpoint."""

    query: str
    market: str
    result_count: int = 0
    results: list[ImageResult] = Field(default_factory=list)


# =============================================================================
# Videos
# =============================================================================


class VideoResult(_BaseModel):
    """One video from Yahoo video search."""

    position: int
    title: str | None = None
    url: str | None = None
    thumbnail_url: str | None = None
    duration: str | None = None
    source: str | None = None
    source_domain: str | None = None
    description: str | None = None
    views: str | None = None


class VideosResponse(_BaseModel):
    """Response from the Yahoo video search endpoint."""

    query: str
    market: str
    result_count: int = 0
    results: list[VideoResult] = Field(default_factory=list)


# =============================================================================
# News
# =============================================================================


class NewsArticle(_BaseModel):
    """One article from the Yahoo news vertical.

    ``published`` is the *relative* age string as rendered by Yahoo, e.g.
    ``"26 minutes ago"``. Yahoo News shows no absolute date, so there is no
    parsed timestamp field.
    """

    position: int
    title: str
    url: str | None = None
    source: str | None = None
    via: str | None = None
    snippet: str | None = None
    published: str | None = None
    thumbnail_url: str | None = None


class NewsResponse(_BaseModel):
    """Response from the Yahoo news endpoint."""

    query: str
    market: str
    total_results: int | None = None
    total_results_text: str | None = None
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
    """A supported Yahoo market."""

    code: str
    name: str
    country: str
    host: str


class MarketsResponse(_BaseModel):
    """All supported Yahoo markets."""

    result_count: int = 0
    markets: list[Market] = Field(default_factory=list)
