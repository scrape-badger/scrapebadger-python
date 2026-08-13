"""Google Ads Transparency Center API client.

Ads Transparency endpoints: search_ads (creatives by advertiser, domain or free
text), get_creative (one creative in full), search_advertisers (resolve a name
or domain to advertiser IDs) and get_advertiser (identity plus disclosed spend).
All methods are async and return strongly-typed Pydantic models.

Filter honesty: ``region``, ``advertiser_id`` and ``query`` are pushed into the
upstream RPC; ``format`` and the date window are applied over the parsed page.
``platform`` and ``political`` cannot be applied upstream yet — both are
validated and reported back under ``filters_applied`` so a caller can see they
were not honoured.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from scrapebadger.google_ads.models import (
    AdCreativeResponse,
    AdsSearchResponse,
    AdvertiserResponse,
    AdvertisersResponse,
)

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient

AdFormat = Literal["TEXT", "IMAGE", "VIDEO"]
AdPlatform = Literal["SEARCH", "MAPS", "PLAY", "SHOPPING", "YOUTUBE"]


class GoogleAdsClient:
    """Client for all Google Ads Transparency Center API operations.

    Example:
        ```python
        from scrapebadger import ScrapeBadger

        async with ScrapeBadger(api_key="your-key") as client:
            # Resolve a domain to advertiser IDs
            found = await client.google_ads.search_advertisers("tesla.com")
            advertiser_id = found.advertisers[0].advertiser_id

            # Their creatives
            ads = await client.google_ads.search_ads(
                advertiser_id=advertiser_id, region="US", format="VIDEO"
            )
            for creative in ads.creatives:
                print(creative.creative_id, creative.first_shown_at)

            # One creative in full
            detail = await client.google_ads.get_creative(
                advertiser_id, ads.creatives[0].creative_id
            )

            # Disclosed spend
            profile = await client.google_ads.get_advertiser(advertiser_id)
            print(profile.spend, profile.currency)
        ```

    Note:
        This client is not instantiated directly. Instead, access it through
        the `google_ads` property of the main `ScrapeBadger` client.
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize Google Ads Transparency client.

        Args:
            client: The base HTTP client for making API requests.
        """
        self._client = client

    async def search_ads(
        self,
        *,
        advertiser_id: str | None = None,
        query: str | None = None,
        region: str = "US",
        platform: AdPlatform | None = None,
        format: AdFormat | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        political: bool = False,
        num: int = 40,
        cursor: str | None = None,
    ) -> AdsSearchResponse:
        """Search creatives by advertiser, domain or free text.

        One of ``advertiser_id`` or ``query`` is required.

        Args:
            advertiser_id: Advertiser ID as shown in the Transparency Center
                URL, e.g. "AR01614014350098432001".
            query: Free text — an advertiser name or a verified domain such as
                "tesla.com".
            region: ISO 3166-1 alpha-2 region the ad was served in ("US", "DE",
                "GB", …), or "anywhere" for no region filter. Defaults to "US".
            platform: Surface the ad ran on — "SEARCH", "MAPS", "PLAY",
                "SHOPPING" or "YOUTUBE". Validated but NOT yet applied
                upstream; see ``filters_applied.platform``.
            format: Creative format — "TEXT", "IMAGE" or "VIDEO".
            start_date: Only creatives still running on/after this date
                (YYYY-MM-DD).
            end_date: Only creatives first shown on/before this date
                (YYYY-MM-DD).
            political: Restrict to political ads. Validated but NOT yet applied
                upstream; see ``filters_applied.political``.
            num: Results per page (1-100). Defaults to 40.
            cursor: ``next_page_token`` from a previous response.

        Returns:
            Search response with the matching creatives and which filters were
            actually honoured.

        Raises:
            ValidationError: If neither ``advertiser_id`` nor ``query`` is
                given, or a filter value is unknown.
            AuthenticationError: If the API key is invalid.

        Example:
            ```python
            ads = await client.google_ads.search_ads(
                query="tesla.com", region="DE", format="IMAGE"
            )
            print(ads.filters_applied.platform)  # False — not honoured upstream
            ```
        """
        params: dict[str, Any] = {
            "advertiser_id": advertiser_id,
            "query": query,
            "region": region,
            "platform": platform,
            "format": format,
            "start_date": start_date,
            "end_date": end_date,
            "political": political,
            "num": num,
            "cursor": cursor,
        }
        response = await self._client.get("/v1/google/ads/search", params=params)
        return AdsSearchResponse.model_validate(response)

    async def get_creative(
        self,
        advertiser_id: str,
        creative_id: str,
        *,
        region: str = "US",
        political: bool = False,
    ) -> AdCreativeResponse:
        """Get full detail for a single creative: media, variations, dates, domain.

        Args:
            advertiser_id: Advertiser ID, e.g. "AR01614014350098432001".
            creative_id: Creative ID, e.g. "CR10484731423840108545".
            region: ISO 3166-1 alpha-2 region, or "anywhere". Defaults to "US".
            political: Also fetch the advertiser's political-ad spend
                disclosure for ``region``. Costs one extra upstream call and is
                empty for non-political advertisers.

        Returns:
            Creative response with every rendered variation.

        Raises:
            NotFoundError: If the creative doesn't exist for the advertiser.
            AuthenticationError: If the API key is invalid.

        Example:
            ```python
            detail = await client.google_ads.get_creative(
                "AR01614014350098432001", "CR10484731423840108545"
            )
            for variation in detail.variations:
                print(variation.width, variation.height, variation.media_url)
            ```
        """
        params: dict[str, Any] = {
            "advertiser_id": advertiser_id,
            "creative_id": creative_id,
            "region": region,
            "political": political,
        }
        response = await self._client.get("/v1/google/ads/creative", params=params)
        return AdCreativeResponse.model_validate(response)

    async def search_advertisers(
        self,
        query: str,
        *,
        region: str = "US",
        num: int = 10,
    ) -> AdvertisersResponse:
        """Resolve an advertiser name or domain to advertiser IDs.

        Args:
            query: Advertiser name or domain to autocomplete (2+ characters).
            region: ISO 3166-1 alpha-2 region, or "anywhere". Defaults to "US".
            num: Suggestions to return (1-20). Defaults to 10.

        Returns:
            Advertisers response with matching advertisers and their IDs.

        Raises:
            ValidationError: If the query is too short.
            AuthenticationError: If the API key is invalid.

        Example:
            ```python
            found = await client.google_ads.search_advertisers("tesla")
            for advertiser in found.advertisers:
                print(advertiser.advertiser_id, advertiser.name, advertiser.domain)
            ```
        """
        params: dict[str, Any] = {"query": query, "region": region, "num": num}
        response = await self._client.get("/v1/google/ads/advertisers", params=params)
        return AdvertisersResponse.model_validate(response)

    async def get_advertiser(
        self,
        advertiser_id: str,
        *,
        region: str = "US",
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> AdvertiserResponse:
        """Get advertiser identity plus disclosed spend and ad mix for one region.

        Args:
            advertiser_id: Advertiser ID, e.g. "AR01614014350098432001".
            region: ISO 3166-1 alpha-2 region. Spend disclosure is
                region-scoped — "anywhere" returns nothing, so it falls back to
                "US". Defaults to "US".
            start_date: Window start (YYYY-MM-DD). Defaults to 30 days ago.
            end_date: Window end (YYYY-MM-DD). Defaults to today.

        Returns:
            Advertiser response with disclosed spend, ad mix and a daily
            spend series.

        Raises:
            NotFoundError: If there is no disclosure for the advertiser in the
                region and window.
            AuthenticationError: If the API key is invalid.

        Example:
            ```python
            profile = await client.google_ads.get_advertiser(
                "AR01614014350098432001", region="US", start_date="2026-07-01"
            )
            for point in profile.spend_by_date:
                print(point.date, point.spend)
            ```
        """
        params: dict[str, Any] = {
            "advertiser_id": advertiser_id,
            "region": region,
            "start_date": start_date,
            "end_date": end_date,
        }
        response = await self._client.get("/v1/google/ads/advertiser", params=params)
        return AdvertiserResponse.model_validate(response)
