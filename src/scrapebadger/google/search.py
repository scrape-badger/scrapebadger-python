"""Google Web Search (SERP) client."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

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
                into `ai_overview`. Adds ~1s and 1 credit when the SERP
                actually defers the overview; no-op otherwise.

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
        return await self._client.get("/v1/google/search", params=params)
