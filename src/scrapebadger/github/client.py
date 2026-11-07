"""Public GitHub compatibility adapter with repository detail."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from urllib.parse import quote

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class GithubClient:
    """Public profile operations and repository detail."""

    def __init__(self, client: BaseClient) -> None:
        self._client = client

    async def get_repository(self, owner: str, repo: str) -> dict[str, Any]:
        """Get public default-branch repository detail. No query options are accepted."""
        if owner in {".", ".."} or repo in {".", ".."}:
            raise ValueError("owner and repo must not be dot path segments")
        return await self._client.get(
            f"/v1/github/repositories/{quote(owner, safe='')}/{quote(repo, safe='')}"
        )

    async def get_profile(
        self,
        username: str,
        *,
        tab: str = "overview",
        year: str | None = None,
        page: str | None = None,
        next_page_token: str | None = None,
    ) -> dict[str, Any]:
        """Get profile.

        Generated from the OpenAPI spec; returns the raw response dict.
        """
        params = {
            k: v
            for k, v in {
                "tab": tab,
                "year": year,
                "page": page,
                "next_page_token": next_page_token,
            }.items()
            if v is not None
        }
        return await self._client.get(f"/v1/github/profiles/{username}", params=params)
