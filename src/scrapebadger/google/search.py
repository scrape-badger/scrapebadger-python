"""Google Web Search (SERP) client."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, overload

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

    @overload
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
        expand_related_questions: bool | int | None = None,
        mode: Literal["full", "fast"] = "full",
        google_domain: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        radius: float | None = None,
        color_scheme: Literal["light", "dark"] | None = None,
        tbm: Literal["isch", "lcl", "vid", "nws", "shop", "pts", "bks"] | None = None,
        udm: str | None = None,
        no_cache: bool = False,
        as_dt: str | None = None,
        as_epq: str | None = None,
        as_eq: str | None = None,
        as_lq: str | None = None,
        as_nlo: str | None = None,
        as_nhi: str | None = None,
        as_oq: str | None = None,
        as_q: str | None = None,
        as_qdr: str | None = None,
        as_rq: str | None = None,
        as_sitesearch: str | None = None,
        user_agent: str | None = None,
        output: Literal["html"],
    ) -> str: ...

    @overload
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
        expand_related_questions: bool | int | None = None,
        mode: Literal["full", "fast"] = "full",
        google_domain: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        radius: float | None = None,
        color_scheme: Literal["light", "dark"] | None = None,
        tbm: Literal["isch", "lcl", "vid", "nws", "shop", "pts", "bks"] | None = None,
        udm: str | None = None,
        no_cache: bool = False,
        as_dt: str | None = None,
        as_epq: str | None = None,
        as_eq: str | None = None,
        as_lq: str | None = None,
        as_nlo: str | None = None,
        as_nhi: str | None = None,
        as_oq: str | None = None,
        as_q: str | None = None,
        as_qdr: str | None = None,
        as_rq: str | None = None,
        as_sitesearch: str | None = None,
        user_agent: str | None = None,
        output: Literal["json"] = "json",
    ) -> dict[str, Any]: ...

    @overload
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
        expand_related_questions: bool | int | None = None,
        mode: Literal["full", "fast"] = "full",
        google_domain: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        radius: float | None = None,
        color_scheme: Literal["light", "dark"] | None = None,
        tbm: Literal["isch", "lcl", "vid", "nws", "shop", "pts", "bks"] | None = None,
        udm: str | None = None,
        no_cache: bool = False,
        as_dt: str | None = None,
        as_epq: str | None = None,
        as_eq: str | None = None,
        as_lq: str | None = None,
        as_nlo: str | None = None,
        as_nhi: str | None = None,
        as_oq: str | None = None,
        as_q: str | None = None,
        as_qdr: str | None = None,
        as_rq: str | None = None,
        as_sitesearch: str | None = None,
        user_agent: str | None = None,
        output: Literal["json", "html"],
    ) -> dict[str, Any] | str: ...

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
        expand_related_questions: bool | int | None = None,
        mode: Literal["full", "fast"] = "full",
        google_domain: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        radius: float | None = None,
        color_scheme: Literal["light", "dark"] | None = None,
        tbm: Literal["isch", "lcl", "vid", "nws", "shop", "pts", "bks"] | None = None,
        udm: str | None = None,
        no_cache: bool = False,
        as_dt: str | None = None,
        as_epq: str | None = None,
        as_eq: str | None = None,
        as_lq: str | None = None,
        as_nlo: str | None = None,
        as_nhi: str | None = None,
        as_oq: str | None = None,
        as_q: str | None = None,
        as_qdr: str | None = None,
        as_rq: str | None = None,
        as_sitesearch: str | None = None,
        user_agent: str | None = None,
        output: Literal["json", "html"] = "json",
    ) -> dict[str, Any] | str:
        """Search Google and get a structured SERP response.

        Args:
            google_domain: Alias for domain; Google requests use google.com with country targeting.
            lat: Latitude; supply together with lon instead of location or uule.
            lon: Longitude; supply together with lat.
            radius: Accuracy in meters; needs lat/lon or a city with a known center.
            color_scheme: Google color scheme.
            tbm: Search type; use output=html or the dedicated vertical APIs.
            udm: Google result filter: 14 web, 18 forums. Other verticals require output=html.
            no_cache: Bypass result caches and request a fresh Google fetch.
            as_dt: Site restriction mode: i includes, e excludes as_sitesearch.
            as_epq: Exact phrase.
            as_eq: Words to exclude.
            as_lq: Find pages linking to this URL; availability depends on Google.
            as_nlo: Numeric range minimum.
            as_nhi: Numeric range maximum.
            as_oq: Match any of these words.
            as_q: Additional query words.
            as_qdr: Time range, such as d, w, m or y1.
            as_rq: Related URL; availability depends on Google.
            as_sitesearch: Restrict results to a site.
            user_agent: Custom User-Agent override.
            output: json returns structured results; html returns the raw page.
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
            expand_related_questions: Open the People Also Ask questions
                and return their answers. ``True`` opens every question the
                page shows (usually four), an integer ``N`` opens the first
                N (0-99; ``0`` or ``False`` opens none). Each answered
                question in ``related_questions`` then carries
                ``text_blocks`` and ``references``, in the same shape as
                ``ai_overview``. The answers are fetched on the same session
                that served the SERP, so there is no way to expand a
                question later; a question whose answer did not come back
                keeps them ``None``. Each answered question bills as one
                more Search request (credits = 20 x (1 + answered) at
                today's price); a question that does not come back is not
                billed. Adds about a second per question. Upgrades
                ``mode="fast"`` to ``"full"``. Not accepted by
                ``/v1/google/light/search``.
            mode: ``"full"`` (default) returns the complete SERP with every
                block — organic, ads, knowledge graph, People Also Ask, AI
                Overview, local pack, news, related searches, videos.
                ``"fast"`` (~30-50% faster cold) hits Google's lite
                ``gbv=1`` endpoint and returns only organic results +
                related searches. Rich blocks (KG, local, AI Overview, news)
                are not returned. Auto-upgrades to ``"full"`` when
                ``ai_overview=True`` or ``expand_related_questions`` is set.
                ``"fast"`` has a 12-second processing budget; past it the
                API returns ``503`` with ``Retry-After: 60``.

        A full-mode query with a ``site:`` operator is answered from
        Google's Web tab: ``organic_results``, ``related_searches`` and
        ``pagination`` only, rich blocks empty (pass ``ai_overview=True``
        for the full page). When Google explicitly finds nothing,
        ``organic_results`` is empty and
        ``search_information.organic_results_state`` is ``"no_results"``;
        when it drops quotes to find results, it is
        ``"Results for relaxed query"``.

        Returns:
            Structured SERP response containing:
            - `search_information`: total_results, time_taken, query_displayed,
              organic_results_state
            - `organic_results`: position/title/link/snippet/displayed_link,
              plus `date`, `sitelinks`, `rich_snippet` and `read_more_link`
              when Google shows them
            - `ads`, `knowledge_graph`, `related_searches`,
              `people_also_search_for`
            - `related_questions`: question, rank, `type` (``"ai_overview"``
              or ``None``), and `text_blocks` / `references` when expanded
            - `ai_overview`: `text_blocks` (paragraph, heading and list
              blocks; list blocks carry `list_items`) with
              `reference_indexes` (0-based into `references`), and
              `references` (title, link, source, snippet, logo)
            - `shopping_results`: position, category, title, price,
              extracted_price, original_price, extracted_original_price,
              source, rating, reviews, delivery, extensions, thumbnail,
              product_id, catalog_id, product_link,
              scrapebadger_product_detail_link
            - `perspectives`, `discussions_and_forums`, `short_videos`,
              `things_to_know`
            - `local_results`, `inline_videos`
            - `pagination`
        """
        params: dict[str, Any] = {
            "google_domain": google_domain,
            "lat": lat,
            "lon": lon,
            "radius": radius,
            "color_scheme": color_scheme,
            "tbm": tbm,
            "udm": udm,
            "no_cache": no_cache,
            "as_dt": as_dt,
            "as_epq": as_epq,
            "as_eq": as_eq,
            "as_lq": as_lq,
            "as_nlo": as_nlo,
            "as_nhi": as_nhi,
            "as_oq": as_oq,
            "as_q": as_q,
            "as_qdr": as_qdr,
            "as_rq": as_rq,
            "as_sitesearch": as_sitesearch,
            "user_agent": user_agent,
            "output": output,
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
        if expand_related_questions is True:
            params["expand_related_questions"] = "true"
        elif expand_related_questions:  # an int N; None, False and 0 open none
            if not 0 < expand_related_questions <= 99:
                raise ValueError("expand_related_questions must be True or an integer 0-99")
            params["expand_related_questions"] = expand_related_questions
        if mode != "full":
            params["mode"] = mode
        if output == "html":
            body, _, _ = await self._client.get_raw("/v1/google/search", params=params)
            return body.decode("utf-8")
        return await self._client.get("/v1/google/search", params=params)

    @overload
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
        device: str | None = None,
        lr: str | None = None,
        tbs: str | None = None,
        uule: str | None = None,
        filter: int | None = None,
        nfpr: int | None = None,
        cr: str | None = None,
        ludocid: str | None = None,
        lsig: str | None = None,
        kgmid: str | None = None,
        si: str | None = None,
        ibp: str | None = None,
        uds: str | None = None,
        google_domain: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        radius: float | None = None,
        color_scheme: Literal["light", "dark"] | None = None,
        tbm: Literal["isch", "lcl", "vid", "nws", "shop", "pts", "bks"] | None = None,
        udm: str | None = None,
        no_cache: bool = False,
        as_dt: str | None = None,
        as_epq: str | None = None,
        as_eq: str | None = None,
        as_lq: str | None = None,
        as_nlo: str | None = None,
        as_nhi: str | None = None,
        as_oq: str | None = None,
        as_q: str | None = None,
        as_qdr: str | None = None,
        as_rq: str | None = None,
        as_sitesearch: str | None = None,
        user_agent: str | None = None,
        output: Literal["html"],
    ) -> str: ...

    @overload
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
        device: str | None = None,
        lr: str | None = None,
        tbs: str | None = None,
        uule: str | None = None,
        filter: int | None = None,
        nfpr: int | None = None,
        cr: str | None = None,
        ludocid: str | None = None,
        lsig: str | None = None,
        kgmid: str | None = None,
        si: str | None = None,
        ibp: str | None = None,
        uds: str | None = None,
        google_domain: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        radius: float | None = None,
        color_scheme: Literal["light", "dark"] | None = None,
        tbm: Literal["isch", "lcl", "vid", "nws", "shop", "pts", "bks"] | None = None,
        udm: str | None = None,
        no_cache: bool = False,
        as_dt: str | None = None,
        as_epq: str | None = None,
        as_eq: str | None = None,
        as_lq: str | None = None,
        as_nlo: str | None = None,
        as_nhi: str | None = None,
        as_oq: str | None = None,
        as_q: str | None = None,
        as_qdr: str | None = None,
        as_rq: str | None = None,
        as_sitesearch: str | None = None,
        user_agent: str | None = None,
        output: Literal["json"] = "json",
    ) -> dict[str, Any]: ...

    @overload
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
        device: str | None = None,
        lr: str | None = None,
        tbs: str | None = None,
        uule: str | None = None,
        filter: int | None = None,
        nfpr: int | None = None,
        cr: str | None = None,
        ludocid: str | None = None,
        lsig: str | None = None,
        kgmid: str | None = None,
        si: str | None = None,
        ibp: str | None = None,
        uds: str | None = None,
        google_domain: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        radius: float | None = None,
        color_scheme: Literal["light", "dark"] | None = None,
        tbm: Literal["isch", "lcl", "vid", "nws", "shop", "pts", "bks"] | None = None,
        udm: str | None = None,
        no_cache: bool = False,
        as_dt: str | None = None,
        as_epq: str | None = None,
        as_eq: str | None = None,
        as_lq: str | None = None,
        as_nlo: str | None = None,
        as_nhi: str | None = None,
        as_oq: str | None = None,
        as_q: str | None = None,
        as_qdr: str | None = None,
        as_rq: str | None = None,
        as_sitesearch: str | None = None,
        user_agent: str | None = None,
        output: Literal["json", "html"],
    ) -> dict[str, Any] | str: ...

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
        device: str | None = None,
        lr: str | None = None,
        tbs: str | None = None,
        uule: str | None = None,
        filter: int | None = None,
        nfpr: int | None = None,
        cr: str | None = None,
        ludocid: str | None = None,
        lsig: str | None = None,
        kgmid: str | None = None,
        si: str | None = None,
        ibp: str | None = None,
        uds: str | None = None,
        google_domain: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        radius: float | None = None,
        color_scheme: Literal["light", "dark"] | None = None,
        tbm: Literal["isch", "lcl", "vid", "nws", "shop", "pts", "bks"] | None = None,
        udm: str | None = None,
        no_cache: bool = False,
        as_dt: str | None = None,
        as_epq: str | None = None,
        as_eq: str | None = None,
        as_lq: str | None = None,
        as_nlo: str | None = None,
        as_nhi: str | None = None,
        as_oq: str | None = None,
        as_q: str | None = None,
        as_qdr: str | None = None,
        as_rq: str | None = None,
        as_sitesearch: str | None = None,
        user_agent: str | None = None,
        output: Literal["json", "html"] = "json",
    ) -> dict[str, Any] | str:
        """Google Light Search — organic results + related searches only.

        Calls the dedicated ``/v1/google/light/search`` endpoint, which is
        billed at the Light rate (half of full :meth:`search`; query
        ``/public/pricing`` for the live rate). Skips ads, Knowledge Graph,
        AI Overview, People Also Ask, local pack, news, inline videos and
        shopping. Use when you only need the 10 blue links. Has a 12-second
        processing budget; past it the API returns ``503`` with
        ``Retry-After: 60``. AI Overview and People Also Ask answers
        (``ai_overview``, ``expand_related_questions``) need :meth:`search`.

        Args:
            google_domain: Alias for domain; Google requests use google.com with country targeting.
            lat: Latitude; supply together with lon instead of location or uule.
            lon: Longitude; supply together with lat.
            radius: Accuracy in meters; needs lat/lon or a city with a known center.
            color_scheme: Google color scheme.
            tbm: Search type; use output=html or the dedicated vertical APIs.
            udm: Google result filter: 14 web, 18 forums. Other verticals require output=html.
            no_cache: Bypass result caches and request a fresh Google fetch.
            as_dt: Site restriction mode: i includes, e excludes as_sitesearch.
            as_epq: Exact phrase.
            as_eq: Words to exclude.
            as_lq: Find pages linking to this URL; availability depends on Google.
            as_nlo: Numeric range minimum.
            as_nhi: Numeric range maximum.
            as_oq: Match any of these words.
            as_q: Additional query words.
            as_qdr: Time range, such as d, w, m or y1.
            as_rq: Related URL; availability depends on Google.
            as_sitesearch: Restrict results to a site.
            user_agent: Custom User-Agent override.
            output: json returns structured results; html returns the raw page.
            q: Search query (supports Google operators like `site:`).
            gl: Country code (default "us").
            hl: Language code (default "en").
            num: Results per page (1-100).
            start: Page offset (0, 10, 20, ...).
            domain: Google domain (e.g. "google.com", "google.co.uk").
            location: City-level geo-targeting.
            safe: Safe search ("off", "medium", "high").
            device: "desktop" or "mobile" (server default: desktop).
            lr: Language restrict (e.g. "lang_en").
            tbs: Time filter (e.g. "qdr:d" for past 24h).
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

        Returns:
            ``{search_information, organic_results, related_searches,
            pagination}`` — no ``ai_overview`` / ``knowledge_graph`` /
            ``ads`` / ``local_results`` / ``news_results`` blocks.
            ``search_information.organic_results_state`` is filled, as on
            full Search.
        """
        params: dict[str, Any] = {
            "google_domain": google_domain,
            "lat": lat,
            "lon": lon,
            "radius": radius,
            "color_scheme": color_scheme,
            "tbm": tbm,
            "udm": udm,
            "no_cache": no_cache,
            "as_dt": as_dt,
            "as_epq": as_epq,
            "as_eq": as_eq,
            "as_lq": as_lq,
            "as_nlo": as_nlo,
            "as_nhi": as_nhi,
            "as_oq": as_oq,
            "as_q": as_q,
            "as_qdr": as_qdr,
            "as_rq": as_rq,
            "as_sitesearch": as_sitesearch,
            "user_agent": user_agent,
            "output": output,
            "q": q,
            "gl": gl,
            "hl": hl,
            "num": num,
            "start": start,
            "domain": domain,
            "location": location,
            "safe": safe,
            "device": device,
            "lr": lr,
            "tbs": tbs,
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
        if output == "html":
            body, _, _ = await self._client.get_raw("/v1/google/light/search", params=params)
            return body.decode("utf-8")
        return await self._client.get("/v1/google/light/search", params=params)
