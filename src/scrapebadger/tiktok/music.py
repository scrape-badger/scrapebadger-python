"""TikTok Music API client.

Provides methods for sound/music detail and the videos using a sound.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.tiktok.models import MusicResponse, VideoListResponse

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class MusicClient:
    """Client for TikTok music endpoints (detail, videos).

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            music = await client.tiktok.music.get_detail("6745650783771970561")
            print(music.music.title)

            videos = await client.tiktok.music.get_videos("6745650783771970561")
            for v in videos.videos:
                print(v.description)
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize music client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def get_detail(
        self,
        music_id: str,
        *,
        region: str = "US",
    ) -> MusicResponse:
        """Get TikTok sound/music detail.

        Args:
            music_id: The TikTok music/sound id.
            region: Content region. Defaults to "US".

        Returns:
            Music response with the sound detail and the resolved region.

        Raises:
            NotFoundError: If the sound doesn't exist.
            AuthenticationError: If the API key is invalid.
        """
        params: dict[str, Any] = {"region": region}
        response = await self._client.get(f"/v1/tiktok/music/{music_id}", params=params)
        return MusicResponse.model_validate(response)

    async def get_videos(
        self,
        music_id: str,
        *,
        region: str = "US",
        count: int = 30,
        cursor: str | None = None,
    ) -> VideoListResponse:
        """Get videos using a given TikTok sound.

        Args:
            music_id: The TikTok music/sound id.
            region: Content region. Defaults to "US".
            count: Number of videos to return (1-50). Defaults to 30.
            cursor: Pagination cursor from a prior response's pagination.cursor;
                omit for the first page.

        Returns:
            Video list response with videos and pagination metadata.
        """
        params: dict[str, Any] = {"region": region, "count": count, "cursor": cursor}
        response = await self._client.get(f"/v1/tiktok/music/{music_id}/videos", params=params)
        return VideoListResponse.model_validate(response)
