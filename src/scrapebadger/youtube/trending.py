"""YouTube Trending API client.

Provides methods for the trending videos feed (by category) and trending Shorts.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.youtube.models import TrendingResponse

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class TrendingClient:
    """Client for YouTube trending endpoints (videos, shorts).

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            trending = await client.youtube.trending.trending(type="music")
            for item in trending.items:
                print(item.position, item.title)

            shorts = await client.youtube.trending.shorts(gl="US")
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize trending client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def trending(
        self,
        *,
        type: str = "now",
        gl: str | None = None,
        hl: str | None = None,
        continuation: str | None = None,
    ) -> TrendingResponse:
        """Get the trending videos feed.

        Args:
            type: Trending category ("now", "music", "gaming", "movies"). Defaults to "now".
            gl: Content region (US, GB, DE…).
            hl: UI language.
            continuation: Pagination token from a previous page.

        Returns:
            Trending response with trending items and a continuation token.

        Raises:
            AuthenticationError: If the API key is invalid.

        Example:
            ```python
            trending = await client.youtube.trending.trending(type="gaming", gl="GB")
            ```
        """
        params: dict[str, Any] = {
            "type": type,
            "gl": gl,
            "hl": hl,
            "continuation": continuation,
        }
        response = await self._client.get("/v1/youtube/trending", params=params)
        return TrendingResponse.model_validate(response)

    async def shorts(
        self,
        *,
        gl: str | None = None,
        hl: str | None = None,
        continuation: str | None = None,
    ) -> TrendingResponse:
        """Get the trending Shorts feed.

        Args:
            gl: Content region (US, GB, DE…).
            hl: UI language.
            continuation: Pagination token from a previous page.

        Returns:
            Trending response with trending Shorts and a continuation token.

        Example:
            ```python
            shorts = await client.youtube.trending.shorts(gl="US")
            ```
        """
        params: dict[str, Any] = {"gl": gl, "hl": hl, "continuation": continuation}
        response = await self._client.get("/v1/youtube/trending/shorts", params=params)
        return TrendingResponse.model_validate(response)
