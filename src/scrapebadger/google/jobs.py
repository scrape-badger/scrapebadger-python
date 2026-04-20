"""Google Jobs client."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


JobsMode = Literal["rpc", "serp"]


class JobsClient:
    """Client for Google Jobs search.

    Two data sources are available via ``mode``:

    - ``"rpc"`` (default, ~1-2 s) — Google Careers' own batchexecute
      RPC. Returns structured JSON with rich per-job fields (title,
      company, locations, posted_at ISO, qualifications + responsibilities
      bullets, apply URL). Scope: Google's own openings (~3-4k roles).
    - ``"serp"`` — public Google Jobs vertical (aggregates LinkedIn /
      Indeed / Built In / ZipRecruiter etc). Slower; filterable via
      ``job_type``, ``date_posted``, ``ltype``, ``chips``, ``uds``,
      ``uule``, ``lrad``.

    Example:
        ```python
        jobs = await client.google.jobs.search(
            "software engineer",
            mode="rpc",
            language="en-US",
        )
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        self._client = client

    async def search(
        self,
        q: str,
        *,
        mode: JobsMode = "rpc",
        location: str | None = None,
        gl: str = "us",
        country: str | None = None,
        hl: str = "en",
        language: str | None = None,
        domain: str = "google.com",
        job_type: str | None = None,
        date_posted: str | None = None,
        ltype: str | None = None,
        chips: str | None = None,
        uds: str | None = None,
        uule: str | None = None,
        lrad: str | None = None,
        next_page_token: str | None = None,
    ) -> dict[str, Any]:
        """Search Google Jobs listings.

        Args:
            q: Job title or keywords.
            mode: ``"rpc"`` (default, Google Careers) or ``"serp"``.
            location: City / state / region (SERP mode).
            gl: Country code.
            country: Alias for ``gl``.
            hl: Language code.
            language: Alias for ``hl`` (accepts ``"en-US"`` etc.).
            domain: Google domain for locale-specific results.
            job_type: ``"FULLTIME"`` / ``"PARTTIME"`` / ``"CONTRACTOR"`` /
                ``"INTERN"`` (SERP mode only).
            date_posted: ``"today"`` / ``"3days"`` / ``"week"`` /
                ``"month"`` (SERP mode only).
            ltype: ``"remote"`` / ``"hybrid"`` / ``"onsite"`` /
                ``"work_from_home"`` (SERP mode only).
            chips: Raw Google chip filter string (SERP mode).
            uds: Opaque filter token (SERP mode).
            uule: UULE-encoded location (SERP mode).
            lrad: Search radius in miles (SERP mode).
            next_page_token: Pagination cursor from prior response.
        """
        params: dict[str, Any] = {"q": q, "mode": mode, "gl": gl}
        for key, val in (
            ("location", location),
            ("country", country),
            ("hl", hl),
            ("language", language),
            ("domain", domain),
            ("job_type", job_type),
            ("date_posted", date_posted),
            ("ltype", ltype),
            ("chips", chips),
            ("uds", uds),
            ("uule", uule),
            ("lrad", lrad),
            ("next_page_token", next_page_token),
        ):
            if val is not None:
                params[key] = val
        return await self._client.get("/v1/google/jobs/search", params=params)
