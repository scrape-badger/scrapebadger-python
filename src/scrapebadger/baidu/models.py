"""Pydantic models for Baidu API responses.

These models mirror the backend ``baidu_scraper`` response schema
field-for-field. All models are immutable (frozen) and ignore unknown fields
for forward compatibility.

Every result carries BOTH URLs: ``url`` is the **real target URL** (decoded
from Baidu's ``mu`` attribute) and ``baidu_url`` is the
``baidu.com/link?url=`` tracking redirect. Dates ship raw in ``date`` (Baidu's
own Chinese relative or absolute string) plus ``date_at`` (ISO 8601 date) when
the raw form is unambiguous; Baidu's SERP carries no time-of-day, so there is
deliberately no timestamp field.
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
    """One organic result from a Baidu web SERP."""

    position: int
    """1-based rank on the page."""

    title: str
    """Result title text."""

    url: str | None = None
    """The REAL target URL, decoded from Baidu's ``mu`` attribute."""

    baidu_url: str | None = None
    """Baidu's ``baidu.com/link?url=...`` tracking redirect."""

    display_url: str | None = None
    """The URL as displayed on the result, when Baidu shows one."""

    snippet: str | None = None
    """Result description text."""

    source: str | None = None
    """Site name shown on the result, e.g. ``阿里巴巴1688``."""

    date: str | None = None
    """Baidu's own date string, e.g. ``2026年8月1日`` or ``3天前``."""

    date_at: str | None = None
    """ISO 8601 date (``YYYY-MM-DD``) when ``date`` is unambiguous."""

    thumbnail: str | None = None
    """Thumbnail image URL, when the result carries one."""

    tpl: str | None = None
    """Baidu's result template id, e.g. ``se_com_default``, ``www_index``."""


class RelatedSearch(_BaseModel):
    """One of Baidu's related-search suggestions."""

    query: str
    """The suggested query."""

    url: str | None = None
    """Baidu SERP URL for the suggestion."""


class SearchResponse(_BaseModel):
    """Response from the Baidu web search endpoint."""

    query: str
    """Echo of the requested query."""

    page: int
    """The page returned."""

    num: int
    """Results per page that was requested."""

    total_results: int | None = None
    """Baidu's own reported total (from ``百度为您找到相关结果约N个``)."""

    results: list[OrganicResult] = Field(default_factory=list)
    """Organic results on this page."""

    related_searches: list[RelatedSearch] = Field(default_factory=list)
    """Baidu's related-search suggestions."""

    url: str
    """The baidu.com URL that was fetched."""


# =============================================================================
# News
# =============================================================================


class NewsResult(_BaseModel):
    """One article from the Baidu news vertical."""

    position: int
    """1-based rank on the page."""

    title: str
    """Article headline."""

    url: str | None = None
    """The REAL article URL."""

    baidu_url: str | None = None
    """Baidu's tracking redirect, when present."""

    snippet: str | None = None
    """Article excerpt."""

    source: str | None = None
    """Publisher name, e.g. ``新华网``."""

    date: str | None = None
    """Baidu's own date string, e.g. ``2026年8月1日`` or ``3小时前``."""

    date_at: str | None = None
    """ISO 8601 date (``YYYY-MM-DD``) when ``date`` is unambiguous."""

    thumbnail: str | None = None
    """Article image URL, when present."""


class NewsResponse(_BaseModel):
    """Response from the Baidu news endpoint."""

    query: str
    """Echo of the requested query."""

    page: int
    """The page returned."""

    total_results: int | None = None
    """Baidu's own reported total, when present."""

    results: list[NewsResult] = Field(default_factory=list)
    """Articles on this page."""

    url: str
    """The baidu.com URL that was fetched."""


# =============================================================================
# Images
# =============================================================================


class ImageResult(_BaseModel):
    """One image from Baidu image search."""

    position: int
    """1-based rank on the page."""

    title: str | None = None
    """Image title / caption."""

    image_url: str | None = None
    """Full-size image URL (Baidu's decoded ``objURL``)."""

    thumbnail_url: str | None = None
    """Baidu-hosted thumbnail."""

    middle_url: str | None = None
    """Baidu-hosted mid-size copy."""

    hover_url: str | None = None
    """Baidu-hosted hover-preview copy."""

    width: int | None = None
    """Full-size image width in pixels."""

    height: int | None = None
    """Full-size image height in pixels."""

    type: str | None = None
    """Image format, e.g. ``jpg``."""

    from_url: str | None = None
    """Page the image was found on."""

    from_title: str | None = None
    """Title of the page the image was found on."""


class ImagesResponse(_BaseModel):
    """Response from the Baidu image search endpoint."""

    query: str
    """Echo of the requested query."""

    page: int
    """The page returned (30 images per page)."""

    total_results: int | None = None
    """Baidu's own reported total, when present."""

    results: list[ImageResult] = Field(default_factory=list)
    """Images on this page."""


# =============================================================================
# Autocomplete
# =============================================================================


class Suggestion(_BaseModel):
    """One Baidu search-box suggestion."""

    query: str
    """The suggested query."""

    type: str | None = None
    """Baidu's suggestion type, e.g. ``sug``."""


class AutocompleteResponse(_BaseModel):
    """Response from the Baidu autocomplete endpoint."""

    query: str
    """Echo of the partial term."""

    suggestions: list[Suggestion] = Field(default_factory=list)
    """Baidu's suggestions for the partial term."""
