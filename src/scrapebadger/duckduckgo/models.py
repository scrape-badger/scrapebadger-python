"""Pydantic models for DuckDuckGo API responses.

These models mirror the backend ``duckduckgo_scraper`` response schema
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


class SearchResult(_BaseModel):
    """One organic (or sponsored) web result."""

    title: str | None = None
    url: str | None = None
    snippet: str | None = None
    display_url: str | None = None
    is_ad: bool | None = None


class AbstractBox(_BaseModel):
    """The instant-answer / knowledge box shown above the web results."""

    heading: str | None = None
    text: str | None = None
    url: str | None = None
    image: str | None = None
    source: str | None = None


class SearchResponse(_BaseModel):
    """A page of DuckDuckGo web results plus the optional abstract box."""

    query: str | None = None
    region: str | None = None
    results: list[SearchResult] = Field(default_factory=list)
    abstract: AbstractBox | None = None
    result_count: int | None = None
    has_next: bool | None = None


# =============================================================================
# Images
# =============================================================================


class ImageResult(_BaseModel):
    """One image result."""

    title: str | None = None
    image: str | None = None
    thumbnail: str | None = None
    url: str | None = None
    width: int | None = None
    height: int | None = None
    source: str | None = None
    encoding_format: str | None = None
    discovery_date: str | None = None


class ImageResponse(_BaseModel):
    """A page of image results."""

    query: str | None = None
    region: str | None = None
    results: list[ImageResult] = Field(default_factory=list)
    result_count: int | None = None
    has_next: bool | None = None


# =============================================================================
# News
# =============================================================================


class NewsResult(_BaseModel):
    """One news article."""

    title: str | None = None
    url: str | None = None
    excerpt: str | None = None
    source: str | None = None
    image: str | None = None
    relative_time: str | None = None
    # The DuckDuckGo endpoint sends these the other way round from the rest of
    # the API — `date_utc` is a Unix epoch and `date_at` an ISO-8601 string.
    # Accept either shape so the model keeps parsing if the scraper is ever
    # brought in line with the house convention.
    date_utc: int | str | None = None
    date_at: str | int | None = None
    syndicate: str | None = None


class NewsResponse(_BaseModel):
    """A page of news results."""

    query: str | None = None
    region: str | None = None
    results: list[NewsResult] = Field(default_factory=list)
    result_count: int | None = None
    has_next: bool | None = None


# =============================================================================
# Videos
# =============================================================================


class VideoResult(_BaseModel):
    """One video result."""

    title: str | None = None
    content: str | None = None
    description: str | None = None
    duration: str | None = None
    publisher: str | None = None
    uploader: str | None = None
    published_at: str | None = None
    view_count: int | None = None
    images: dict[str, Any] = Field(default_factory=dict)
    embed_url: str | None = None


class VideoResponse(_BaseModel):
    """A page of video results."""

    query: str | None = None
    region: str | None = None
    results: list[VideoResult] = Field(default_factory=list)
    result_count: int | None = None
    has_next: bool | None = None


# =============================================================================
# Autocomplete
# =============================================================================


class AutocompleteResponse(_BaseModel):
    """Search-box autocomplete suggestions."""

    query: str | None = None
    suggestions: list[str] = Field(default_factory=list)


# =============================================================================
# Instant answer
# =============================================================================


class InstantAnswerTopic(_BaseModel):
    """One related-topic entry in an instant answer."""

    text: str | None = None
    url: str | None = None
    icon: str | None = None


class InstantAnswerResponse(_BaseModel):
    """The DuckDuckGo Instant Answer (zero-click) payload."""

    query: str | None = None
    abstract: str | None = None
    abstract_text: str | None = None
    abstract_source: str | None = None
    abstract_url: str | None = None
    heading: str | None = None
    answer: str | None = None
    answer_type: str | None = None
    definition: str | None = None
    definition_source: str | None = None
    definition_url: str | None = None
    image: str | None = None
    type: str | None = None
    redirect: str | None = None
    related_topics: list[InstantAnswerTopic] = Field(default_factory=list)


# =============================================================================
# Regions (reference)
# =============================================================================


class Region(_BaseModel):
    """A supported DuckDuckGo region."""

    code: str | None = None
    name: str | None = None


class RegionsResponse(_BaseModel):
    """All supported DuckDuckGo regions."""

    regions: list[Region] = Field(default_factory=list)
    count: int | None = None
