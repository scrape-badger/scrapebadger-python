"""Google Ads Transparency Center client."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class AdsClient:
    """Client for Google Ads Transparency Center endpoints.

    Free-text ``search`` is domain-based and will not find a brand by name:
    resolve the name with ``search_advertisers`` first, then pass the
    ``advertiser_id`` on.

    Example:
        ```python
        found = await client.google.ads.search_advertisers("ruffwear", fuzzy=True)
        advertiser_id = found["advertisers"][0]["advertiser_id"]

        ads = await client.google.ads.search(advertiser_id=advertiser_id, format="VIDEO")
        first = ads["creatives"][0]
        creative = await client.google.ads.creative(advertiser_id, first["creative_id"])
        spend = await client.google.ads.advertiser(advertiser_id, region="US")
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        self._client = client

    async def search(
        self,
        query: str | None = None,
        *,
        advertiser_id: str | None = None,
        region: str = "US",
        platform: str | None = None,
        format: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        political: bool = False,
        num: int = 40,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Search ad creatives by advertiser ID, verified domain or free text.

        The response carries ``creatives``, ``total_results``,
        ``next_page_token`` and ``filters_applied``, which says which of the
        requested filters Google actually honoured.

        Args:
            query: An advertiser name or a verified domain such as ``"tesla.com"``.
            advertiser_id: Advertiser ID, e.g. ``"AR01614014350098432001"``.
            region: ISO 3166-1 alpha-2 region, or ``"anywhere"``.
            platform: ``SEARCH``, ``MAPS``, ``PLAY``, ``SHOPPING`` or
                ``YOUTUBE``. Validated but not yet applied upstream — see
                ``filters_applied.platform``.
            format: Creative format: ``TEXT``, ``IMAGE`` or ``VIDEO``.
            start_date: Only creatives still running on/after this date (YYYY-MM-DD).
            end_date: Only creatives first shown on/before this date (YYYY-MM-DD).
            political: Restrict to political ads. Validated but not yet
                applied upstream — see ``filters_applied.political``.
            num: Results per page (1-100).
            cursor: ``next_page_token`` from a previous response.
        """
        params: dict[str, Any] = {"region": region, "num": num}
        if query:
            params["query"] = query
        if advertiser_id:
            params["advertiser_id"] = advertiser_id
        if platform:
            params["platform"] = platform
        if format:
            params["format"] = format
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if political:
            params["political"] = True
        if cursor:
            params["cursor"] = cursor
        return await self._client.get("/v1/google/ads/search", params=params)

    async def search_advertisers(
        self,
        query: str,
        *,
        num: int = 10,
        num_domains: int = 10,
        country: str | None = None,
        region: str = "US",
        fuzzy: bool = False,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Resolve an advertiser name or domain to advertiser IDs.

        Google's own matching has no typo tolerance: names match by word
        prefix and domains by substring. ``fuzzy=True`` also finds misspelled
        and look-alike advertisers; each row then carries ``similarity``
        (0-1 closeness to the query) and ``matched_query`` (the variant or
        look-alike domain that surfaced it), and the response lists the
        ``variants`` searched and ``variants_failed``. ``next_page_token``
        pages the domain rows only; advertisers do not page.

        Args:
            query: Advertiser name or domain (at least 2 characters).
            num: Advertisers to return (1-3000). One call returns every match
                up to this.
            num_domains: Domain rows to return (0-100).
            country: ISO 3166-1 alpha-2: only advertisers registered in this
                country. Domain rows are not filtered.
            region: Echoed on the response only. Use ``country`` to filter.
            fuzzy: Also find misspelled and look-alike advertisers, ranked by
                ``similarity``. Billed as 3 lookups.
            cursor: ``next_page_token`` from a previous response: the next page
                of domain rows. Cannot be combined with ``fuzzy``.
        """
        params: dict[str, Any] = {
            "query": query,
            "num": num,
            "num_domains": num_domains,
            "region": region,
        }
        if country:
            params["country"] = country
        if fuzzy:
            params["fuzzy"] = True
        if cursor:
            params["cursor"] = cursor
        return await self._client.get("/v1/google/ads/advertisers", params=params)

    async def advertiser(
        self,
        advertiser_id: str,
        *,
        region: str = "US",
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict[str, Any]:
        """Get an advertiser's identity plus disclosed spend and ad mix for one region.

        The response carries ``advertiser_name``, ``verified``, ``ads_count``,
        ``spend`` and ``currency``, the ``ad_mix`` by format and a per-day
        ``spend_by_date`` curve.

        Args:
            advertiser_id: Advertiser ID, e.g. ``"AR01614014350098432001"``.
            region: ISO 3166-1 alpha-2 region. Spend disclosure is
                region-scoped, so ``"anywhere"`` falls back to ``"US"``.
            start_date: Window start (YYYY-MM-DD). Defaults to 30 days ago.
            end_date: Window end (YYYY-MM-DD). Defaults to today.
        """
        params: dict[str, Any] = {"advertiser_id": advertiser_id, "region": region}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return await self._client.get("/v1/google/ads/advertiser", params=params)

    async def creative(
        self,
        advertiser_id: str,
        creative_id: str,
        *,
        region: str = "US",
        political: bool = False,
    ) -> dict[str, Any]:
        """Get full detail for one ad creative.

        The response carries the media, every rendered size in
        ``variations``, run dates and, with ``political=True``, the
        advertiser's ``political`` spend disclosure.

        Args:
            advertiser_id: Advertiser ID, e.g. ``"AR01614014350098432001"``.
            creative_id: Creative ID, e.g. ``"CR10484731423840108545"``.
            region: ISO 3166-1 alpha-2 region, or ``"anywhere"``.
            political: Also fetch the advertiser's political-ad spend
                disclosure for ``region``. Empty for non-political advertisers.
        """
        params: dict[str, Any] = {
            "advertiser_id": advertiser_id,
            "creative_id": creative_id,
            "region": region,
        }
        if political:
            params["political"] = True
        return await self._client.get("/v1/google/ads/creative", params=params)
