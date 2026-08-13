"""Pydantic models for Google Ads Transparency Center API responses.

These models mirror the backend ``google_scraper.models.ads`` response schema
field-for-field. All models are immutable (frozen) and ignore unknown fields
for forward compatibility.

Every timestamp is exposed twice: ``*_utc`` as unix seconds and ``*_at`` as an
ISO-8601 string in UTC with a ``Z`` suffix.
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
# Creatives
# =============================================================================


class AdCreative(_BaseModel):
    """One creative as returned by a creative search."""

    creative_id: str | None = None
    advertiser_id: str | None = None
    advertiser_name: str | None = None
    target_domain: str | None = None
    format: str | None = None  # TEXT | IMAGE | VIDEO
    media_url: str | None = None
    preview_html: str | None = None
    first_shown_utc: int | None = None
    first_shown_at: str | None = None
    last_shown_utc: int | None = None
    last_shown_at: str | None = None
    days_shown: int | None = None
    details_link: str | None = None


class AppliedFilters(_BaseModel):
    """Which requested filters the upstream RPC actually honoured.

    ``platform`` and ``political`` have no calibrated wire field on the
    Transparency Center RPC, so they are reported here as ``False`` rather than
    silently dropped — a filter that appears to work but doesn't is worse than
    one that says it didn't.
    """

    region: bool = False
    advertiser_id: bool = False
    query: bool = False
    format: bool = False
    date_range: bool = False
    platform: bool = False
    political: bool = False


class AdsSearchResponse(_BaseModel):
    """A page of creatives matching a search."""

    region: str
    total_results: int | None = None
    returned_results: int = 0
    next_page_token: str | None = None
    filters_applied: AppliedFilters = Field(default_factory=AppliedFilters)
    creatives: list[AdCreative] = Field(default_factory=list)


class CreativeVariation(_BaseModel):
    """One rendered size/variant of a creative."""

    media_url: str | None = None
    preview_html: str | None = None
    width: int | None = None
    height: int | None = None


class PoliticalRegionSpend(_BaseModel):
    """Disclosed spend for a political advertiser in one region."""

    region: str | None = None
    currency: str | None = None
    spend: float | None = None
    ads_count: int | None = None


class PoliticalDisclosure(_BaseModel):
    """Political-ad disclosure for a creative's advertiser.

    ``spend_min``/``spend_max`` and the impression bounds are the per-creative
    disclosure ranges the Transparency Center UI shows; their wire fields are
    not calibrated yet and stay ``None`` until they are.
    """

    currency: str | None = None
    spend: float | None = None
    spend_min: float | None = None
    spend_max: float | None = None
    impressions_min: int | None = None
    impressions_max: int | None = None
    ads_count: int | None = None
    regions: list[PoliticalRegionSpend] = Field(default_factory=list)


class AdCreativeResponse(_BaseModel):
    """Full detail for a single creative: media, variations, dates, domain."""

    creative_id: str | None = None
    advertiser_id: str | None = None
    advertiser_name: str | None = None
    target_domain: str | None = None
    region: str
    format: str | None = None  # TEXT | IMAGE | VIDEO
    media_url: str | None = None
    first_shown_utc: int | None = None
    first_shown_at: str | None = None
    last_shown_utc: int | None = None
    last_shown_at: str | None = None
    days_shown: int | None = None
    details_link: str | None = None
    variations: list[CreativeVariation] = Field(default_factory=list)
    political: PoliticalDisclosure | None = None


# =============================================================================
# Advertisers
# =============================================================================


class AdvertiserSuggestion(_BaseModel):
    """One advertiser (or bare domain) from the autocomplete search."""

    advertiser_id: str | None = None
    name: str | None = None
    region: str | None = None
    domain: str | None = None
    verified: bool | None = None
    ads_count: int | None = None
    details_link: str | None = None


class AdvertisersResponse(_BaseModel):
    """Advertiser name/domain resolved to advertiser IDs."""

    query: str
    region: str
    advertisers: list[AdvertiserSuggestion] = Field(default_factory=list)


class AdvertiserAdMix(_BaseModel):
    """Share of an advertiser's disclosed spend by creative format."""

    format: str | None = None  # TEXT | IMAGE | VIDEO
    share: float | None = None
    spend: float | None = None


class AdvertiserSpendPoint(_BaseModel):
    """Disclosed spend for one day of the requested window."""

    date: str | None = None  # YYYYMMDD, as Google returns it
    share: float | None = None
    spend: float | None = None


class AdvertiserResponse(_BaseModel):
    """Advertiser identity plus disclosed spend and ad mix for one region."""

    advertiser_id: str
    advertiser_name: str | None = None
    region: str
    verified: bool | None = None
    ads_count: int | None = None
    currency: str | None = None
    spend: float | None = None
    start_date: str | None = None
    end_date: str | None = None
    details_link: str | None = None
    ad_mix: list[AdvertiserAdMix] = Field(default_factory=list)
    spend_by_date: list[AdvertiserSpendPoint] = Field(default_factory=list)
