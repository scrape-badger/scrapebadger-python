"""Google Jobs client."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class JobsClient:
    """Client for Google Jobs search.

    Example:
        ```python
        jobs = await client.google.jobs.search(
            "software engineer",
            location="San Francisco, CA",
            job_type="FULLTIME",
            date_posted="week",
        )
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        self._client = client

    async def search(
        self,
        q: str,
        *,
        location: str | None = None,
        gl: str = "us",
        job_type: str | None = None,
        date_posted: str | None = None,
    ) -> dict[str, Any]:
        """Search Google Jobs listings.

        Args:
            q: Job title or keywords.
            location: City / state / region.
            gl: Country code.
            job_type: One of "FULLTIME", "PARTTIME", "CONTRACTOR", "INTERN".
            date_posted: One of "today", "3days", "week", "month".
        """
        params: dict[str, Any] = {"q": q, "gl": gl}
        if location:
            params["location"] = location
        if job_type:
            params["job_type"] = job_type
        if date_posted:
            params["date_posted"] = date_posted
        return await self._client.get("/v1/google/jobs/search", params=params)
