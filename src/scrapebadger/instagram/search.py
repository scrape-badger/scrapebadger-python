"""Instagram Search API client.

Searches users, hashtags, places, the "top" blended results, reels, and music,
plus a lightweight autocomplete/typeahead.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.instagram.models import (
    Audio,
    Hashtag,
    Location,
    Media,
    Paginated,
    UserShort,
)

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class SearchClient:
    """Client for Instagram search endpoints.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            users = await client.instagram.search.users("nike")
            for user in users.items:
                print(f"@{user.username}: {user.full_name}")

            tags = await client.instagram.search.hashtags("running")
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        self._client = client

    async def users(self, query: str) -> Paginated[UserShort]:
        """Temporarily unavailable: authenticated Instagram data is temporarily offline.

        Search accounts by name/username.
        """
        return await self._search("users", query, UserShort)

    async def hashtags(self, query: str) -> Paginated[Hashtag]:
        """Search hashtags."""
        return await self._search("hashtags", query, Hashtag)

    async def places(self, query: str) -> Paginated[Location]:
        """Temporarily unavailable: authenticated Instagram data is temporarily offline.

        Search places/locations.
        """
        return await self._search("places", query, Location)

    async def reels(self, query: str) -> Paginated[Media]:
        """Temporarily unavailable: authenticated Instagram data is temporarily offline.

        Search reels.
        """
        return await self._search("reels", query, Media)

    async def music(self, query: str) -> Paginated[Audio]:
        """Temporarily unavailable: authenticated Instagram data is temporarily offline.

        Search music/audio tracks.
        """
        return await self._search("music", query, Audio)

    async def top(self, query: str) -> dict[str, Any]:
        """Get blended "top" results (users, hashtags, and places).

        Returns the raw envelope — the top tab mixes entity types, so it is
        surfaced as-is rather than a single typed list.
        """
        params: dict[str, Any] = {"query": query}
        return await self._client.get("/v1/instagram/search/top", params=params)

    async def autocomplete(self, query: str) -> dict[str, Any]:
        """Temporarily unavailable: authenticated Instagram data is temporarily offline.

        Get typeahead/autocomplete suggestions (mixed entity types).
        """
        params: dict[str, Any] = {"query": query}
        return await self._client.get("/v1/instagram/search/autocomplete", params=params)

    async def _search(self, kind: str, query: str, model: type[Any]) -> Paginated[Any]:
        params: dict[str, Any] = {"query": query}
        response = await self._client.get(f"/v1/instagram/search/{kind}", params=params)
        return Paginated[model].model_validate(response)  # type: ignore[valid-type]
