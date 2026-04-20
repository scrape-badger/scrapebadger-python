"""Google Web Search (SERP) client."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class SearchClient:
    """Client for Google Web Search.

    Example:
        ```python
        serp = await client.google.search.search("python 3.13")
        for result in serp["organic_results"]:
            print(result["title"], result["link"])
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        self._client = client

    async def search(
        self,
        q: str,
        *,
        gl: str = "us",
        hl: str = "en",
        num: int = 10,
        start: int = 0,
        domain: str = "google.com",
        device: str = "desktop",
        location: str | None = None,
        lr: str | None = None,
        tbs: str | None = None,
        safe: str = "off",
        uule: str | None = None,
        filter: int | None = None,
        nfpr: int = 0,
        cr: str | None = None,
        ludocid: str | None = None,
        lsig: str | None = None,
        kgmid: str | None = None,
        si: str | None = None,
        ibp: str | None = None,
        uds: str | None = None,
        ai_overview: bool = False,
        mode: Literal["full", "fast"] = "full",
    ) -> dict[str, Any]:
        """Search Google and get a structured SERP response.

        Args:
            q: Search query (supports Google operators like `site:`, `intitle:`).
            gl: Country code (default "us").
            hl: Language code (default "en").
            num: Results per page (1-100).
            start: Page offset (0, 10, 20, ...).
            domain: Google domain (e.g. "google.com", "google.co.uk").
            device: "desktop" or "mobile".
            location: City-level geo-targeting.
            lr: Language restrict (e.g. "lang_en").
            tbs: Time filter (e.g. "qdr:d" for past 24h).
            safe: Safe search ("off", "medium", "high").
            uule: UULE encoded location.
            filter: Show omitted results when set to 0.
            nfpr: Set to 1 to disable auto-correction.
            cr: Country restrict.
            ludocid: Google Place CID.
            lsig: Knowledge Graph map ID.
            kgmid: Knowledge Graph entity ID.
            si: Cached search params token.
            ibp: Layout control.
            uds: Google filter string.
            ai_overview: When True, chase Google's deferred AI Overview
                page_token with a follow-up fetch and merge the result back
                into `ai_overview`. Adds ~1s when the SERP actually defers
                the overview; no-op otherwise. Credit cost is configured
                per-endpoint by ScrapeBadger admins — query the public
                ``/public/pricing`` API for the live rate.
            mode: ``"full"`` (default) returns the complete SERP with every
                block — organic, ads, knowledge graph, People Also Ask, AI
                Overview, local pack, news, related searches, videos.
                ``"fast"`` (~30-50% faster cold) hits Google's lite
                ``gbv=1`` endpoint and returns only organic results +
                related searches. Rich blocks (KG, local, AI Overview, news)
                are not returned. Auto-upgrades to ``"full"`` when
                ``ai_overview=True``.

        Returns:
            Structured SERP response containing:
            - `search_information`: total_results, time_taken, query_displayed
            - `organic_results`: list of position/title/link/snippet/displayed_link
            - `ads`, `knowledge_graph`, `related_questions`, `related_searches`
            - `local_results`, `inline_videos`, `ai_overview`
            - `pagination`
        """
        params: dict[str, Any] = {
            "q": q,
            "gl": gl,
            "hl": hl,
            "num": num,
            "start": start,
            "domain": domain,
            "device": device,
            "location": location,
            "lr": lr,
            "tbs": tbs,
            "safe": safe,
            "uule": uule,
            "filter": filter,
            "nfpr": nfpr,
            "cr": cr,
            "ludocid": ludocid,
            "lsig": lsig,
            "kgmid": kgmid,
            "si": si,
            "ibp": ibp,
            "uds": uds,
        }
        if ai_overview:
            params["ai_overview"] = True
        if mode != "full":
            params["mode"] = mode
        return await self._client.get("/v1/google/search", params=params)

    async def light(
        self,
        q: str,
        *,
        gl: str = "us",
        hl: str = "en",
        num: int = 10,
        start: int = 0,
        domain: str = "google.com",
        location: str | None = None,
        safe: str = "off",
    ) -> dict[str, Any]:
        """Lightweight Google Search — organic results + related searches only.

        ~40% faster than :meth:`search`. Skips ads, Knowledge Graph,
        AI Overview, local pack, news, inline videos, and shopping.
        Use when you only need the 10 blue links. Credit cost is
        configured per-endpoint by admins — query ``/public/pricing``
        for the live rate.

        Returns:
            ``{search_information, organic_results, related_searches,
            pagination}`` — no ``ai_overview`` / ``knowledge_graph`` /
            ``ads`` / ``local_results`` / ``news_results`` blocks.
        """
        return await self.search(
            q,
            gl=gl,
            hl=hl,
            num=num,
            start=start,
            domain=domain,
            location=location,
            safe=safe,
            mode="fast",
        )
