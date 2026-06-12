"""TikTok Ads API client.

Provides methods for searching the TikTok Commercial Content Library
(EU-DSA ad transparency).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.tiktok.models import AdLibrarySearchResponse

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
