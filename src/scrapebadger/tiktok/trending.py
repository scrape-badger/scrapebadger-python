"""TikTok Trending API client.

Provides methods for trending videos, hashtags, and songs.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.tiktok.models import (
    TrendingHashtagsResponse,
    TrendingSongsResponse,
    VideoListResponse,
)

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class TrendingClient:
    """Client for TikTok trending endpoints (videos, hashtags, songs).

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            videos = await client.tiktok.trending.videos(region="GB")
            for v in videos.videos:
                print(v.description)

            songs = await client.tiktok.trending.songs(region="GB")
            for s in songs.songs:
                print(f"{s.rank}. {s.title}")
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize trending client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def videos(
        self,
        *,
        region: str = "US",
        count: int = 20,
    ) -> VideoListResponse:
        """Get trending videos from the TikTok Explore feed.

        Args:
            region: Content region. Defaults to "US".
            count: Number of videos to return (1-50). Defaults to 20.

        Returns:
            Video list response with trending videos and pagination metadata.
        """
        params: dict[str, Any] = {"region": region, "count": count}
        response = await self._client.get("/v1/tiktok/trending/videos", params=params)
        return VideoListResponse.model_validate(response)

    async def hashtags(
        self,
        *,
        region: str = "US",
        period: int = 7,
        count: int = 20,
    ) -> TrendingHashtagsResponse:
        """Get trending hashtags (mobile Discover surface).

        Args:
            region: Content region. Defaults to "US".
            period: Trailing window in days. Defaults to 7.
            count: Number of hashtags to return (1-50). Defaults to 20.

        Returns:
            Trending hashtags response with ranked hashtags.
        """
        params: dict[str, Any] = {"region": region, "period": period, "count": count}
        response = await self._client.get("/v1/tiktok/trending/hashtags", params=params)
        return TrendingHashtagsResponse.model_validate(response)

    async def songs(
        self,
        *,
        region: str = "US",
        period: int = 7,
        count: int = 20,
    ) -> TrendingSongsResponse:
        """Get trending songs/sounds (mobile hot-music feed — ranked by usage).

        Args:
            region: Content region. Defaults to "US".
            period: Trailing window in days. Defaults to 7.
            count: Number of songs to return (1-50). Defaults to 20.

        Returns:
            Trending songs response with ranked songs.
        """
        params: dict[str, Any] = {"region": region, "period": period, "count": count}
        response = await self._client.get("/v1/tiktok/trending/songs", params=params)
        return TrendingSongsResponse.model_validate(response)
