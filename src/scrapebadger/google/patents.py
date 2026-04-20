"""Google Patents client."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class PatentsClient:
    """Client for Google Patents endpoints.

    Example:
        ```python
        results = await client.google.patents.search("distributed lock")
        first = results["results"][0]
        detail = await client.google.patents.detail(first["patent_id"])
        print(detail["abstract"])
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        self._client = client

    async def search(
        self,
        q: str,
        *,
        page: int = 0,
        num: int = 10,
        sort: str | None = None,
        inventor: str | None = None,
        assignee: str | None = None,
        country: str | None = None,
        language: str | None = None,
        status: str | None = None,
        patent_type: str | None = None,
        before: str | None = None,
        after: str | None = None,
    ) -> dict[str, Any]:
        """Search Google Patents via the ``/xhr/query`` JSON RPC.

        Args:
            q: Query (supports Boolean logic, semicolons for multiple terms).
            page: Page number (0-indexed).
            num: Results per page (1-100).
            sort: ``"new"`` or ``"old"``.
            inventor: Comma-separated inventor names.
            assignee: Comma-separated assignee / company names.
            country: Patent-office country code (``"US"``, ``"EP"``, ``"WO"``, …).
            language: Patent language — ``ENGLISH``, ``GERMAN``, ``CHINESE``,
                ``FRENCH``, ``JAPANESE``, ``KOREAN``, ``SPANISH``.
            status: ``"GRANT"`` or ``"APPLICATION"``.
            patent_type: ``"PATENT"`` or ``"DESIGN"``.
            before: Filing/priority-date upper bound (``YYYYMMDD``).
            after: Filing/priority-date lower bound (``YYYYMMDD``).
        """
        params: dict[str, Any] = {"q": q, "page": page, "num": num}
        if sort:
            params["sort"] = sort
        if inventor:
            params["inventor"] = inventor
        if assignee:
            params["assignee"] = assignee
        if country:
            params["country"] = country
        if language:
            params["language"] = language
        if status:
            params["status"] = status
        if patent_type:
            params["patent_type"] = patent_type
        if before:
            params["before"] = before
        if after:
            params["after"] = after
        return await self._client.get("/v1/google/patents/search", params=params)

    async def detail(
        self,
        patent_id: str,
    ) -> dict[str, Any]:
        """Get rich patent document details by patent number.

        Response carries: full ``abstract``, every ``claim``, complete
        ``description``, structured ``cpc_classifications``
        (``{code, description}``), split ``backward_citations`` /
        ``forward_citations`` (with ``primary_examiner`` flag),
        ``non_patent_citations`` (journal articles), ``concepts``
        (research fields), ``legal_events`` (prosecution history),
        ``figures`` (full-res image URLs + thumbnails), every
        ``inventor`` and the full ``assignees_original`` history.

        Args:
            patent_id: Publication number (e.g. ``"US10000000B2"``).
        """
        params: dict[str, Any] = {"patent_id": patent_id}
        return await self._client.get("/v1/google/patents/detail", params=params)
