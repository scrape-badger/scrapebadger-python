"""TikTok Ads API client.

Provides methods for searching the TikTok Commercial Content Library
(EU-DSA ad transparency).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.tiktok.models import (
    AdDetailResponse,
    AdLibrarySearchResponse,
    AdvertiserSearchResponse,
)

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class AdsClient:
    """Client for the TikTok Ad Library (Commercial Content Library).

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            ads = await client.tiktok.ads.search("sneakers", region="DE")
            for ad in ads.ads:
                print(ad.name)
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize ads client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def search(
        self,
        query: str = "",
        *,
        advertiser_id: str = "",
        region: str = "DE",
        days: int = 30,
        sort: str = "last_shown_date,desc",
        offset: int = 0,
        search_id: str = "",
        count: int = 20,
    ) -> AdLibrarySearchResponse:
        """Search TikTok's Commercial Content Library by keyword or advertiser.

        The Ad Library is EU-only, so ``region`` defaults to ``"DE"``.

        Args:
            query: Keyword (ignored when ``advertiser_id`` is set). Defaults to "".
            advertiser_id: Advertiser business id(s) for an advertiser search.
            region: EU region code. Defaults to "DE".
            days: Trailing window in days (1-365). Defaults to 30.
            sort: Sort order. Defaults to "last_shown_date,desc".
            offset: Result offset for pagination. Defaults to 0.
            search_id: Search id from a previous page (chains pagination).
            count: Number of ads to return (1-50). Defaults to 20.

        Returns:
            Ad library search response with ads and offset pagination metadata.

        Example:
            ```python
            page = await client.tiktok.ads.search("sneakers", region="FR", days=90)
            if page.pagination.has_more:
                more = await client.tiktok.ads.search(
                    "sneakers",
                    region="FR",
                    offset=page.pagination.offset,
                    search_id=page.pagination.search_id or "",
                )
            ```
        """
        params: dict[str, Any] = {
            "query": query,
            "advertiser_id": advertiser_id,
            "region": region,
            "days": days,
            "sort": sort,
            "offset": offset,
            "search_id": search_id,
            "count": count,
        }
        response = await self._client.get("/v1/tiktok/ads/search", params=params)
        return AdLibrarySearchResponse.model_validate(response)

    async def search_advertisers(
        self,
        query: str,
        *,
        region: str = "DE",
        count: int = 10,
    ) -> AdvertiserSearchResponse:
        """Look up advertiser business ids by name.

        Feed the returned ``id`` into :meth:`search` as ``advertiser_id`` to list all of an
        advertiser's ads. Matching is on the legal entity name, so a brand may appear under
        several legal entities.

        Args:
            query: Advertiser name (or partial) to look up.
            region: EU region code. Defaults to "DE".
            count: Max suggestions (1-50). Defaults to 10.

        Returns:
            Matching advertisers, each with a business ``id``.

        Example:
            ```python
            res = await client.tiktok.ads.search_advertisers("nike", region="DE")
            ads = await client.tiktok.ads.search(advertiser_id=res.advertisers[0].id)
            ```
        """
        params: dict[str, Any] = {"query": query, "region": region, "count": count}
        response = await self._client.get("/v1/tiktok/ads/advertisers", params=params)
        return AdvertiserSearchResponse.model_validate(response)

    async def get_detail(
        self,
        ad_id: str,
        *,
        region: str = "DE",
    ) -> AdDetailResponse:
        """Fetch a single ad's advertiser, creatives, and full targeting/impression breakdown.

        Args:
            ad_id: Ad id from an :meth:`search` result.
            region: EU region code. Defaults to "DE".

        Returns:
            The ad, its advertiser, and per-region age/gender impression targeting.

        Example:
            ```python
            detail = await client.tiktok.ads.get_detail("1873163420032386", region="DE")
            print(detail.advertiser.adv_biz_ids, detail.targeting.target_audience_size)
            ```
        """
        params: dict[str, Any] = {"region": region}
        response = await self._client.get(f"/v1/tiktok/ads/{ad_id}", params=params)
        return AdDetailResponse.model_validate(response)
