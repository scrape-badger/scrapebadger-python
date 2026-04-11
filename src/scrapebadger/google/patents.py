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
    ) -> dict[str, Any]:
        """Search Google Patents.

        Args:
            q: Query (supports Boolean logic, semicolons for multiple terms).
            page: Page number (0-indexed).
            num: Results per page (1-100).
            sort: "new" or "old".
            inventor: Comma-separated inventor names.
            assignee: Comma-separated assignee names.
        """
        params: dict[str, Any] = {"q": q, "page": page, "num": num}
        if sort:
            params["sort"] = sort
        if inventor:
            params["inventor"] = inventor
        if assignee:
            params["assignee"] = assignee
        return await self._client.get("/v1/google/patents/search", params=params)

    async def detail(
        self,
        patent_id: str,
    ) -> dict[str, Any]:
        """Get patent document details by patent number."""
        params: dict[str, Any] = {"patent_id": patent_id}
        return await self._client.get("/v1/google/patents/detail", params=params)
