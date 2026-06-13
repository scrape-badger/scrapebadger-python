"""TikTok Hashtags API client.

Provides methods for hashtag/challenge detail and the videos tagged with a
hashtag.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.tiktok.models import HashtagResponse, VideoListResponse

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class HashtagsClient:
    """Client for TikTok hashtag endpoints (detail, videos).

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            tag = await client.tiktok.hashtags.get_detail("fyp")
            print(tag.hashtag.view_count)

            videos = await client.tiktok.hashtags.get_videos("fyp")
            for v in videos.videos:
                print(v.description)
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize hashtags client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def get_detail(
        self,
        name: str,
        *,
        region: str = "US",
    ) -> HashtagResponse:
        """Get TikTok hashtag/challenge detail.

        Args:
            name: The hashtag name (without the leading '#').
            region: Content region. Defaults to "US".

        Returns:
            Hashtag response with the hashtag detail and the resolved region.

        Raises:
            NotFoundError: If the hashtag doesn't exist.
            AuthenticationError: If the API key is invalid.
        """
        params: dict[str, Any] = {"region": region}
        response = await self._client.get(f"/v1/tiktok/hashtags/{name}", params=params)
        return HashtagResponse.model_validate(response)

    async def get_videos(
        self,
        name: str,
        *,
        region: str = "US",
        count: int = 30,
        cursor: str | None = None,
    ) -> VideoListResponse:
        """Get videos tagged with a TikTok hashtag.

        Args:
            name: The hashtag name (without the leading '#').
            region: Content region. Defaults to "US".
            count: Number of videos to return (1-50). Defaults to 30.
            cursor: Pagination cursor from a prior response's pagination.cursor;
                omit for the first page.

        Returns:
            Video list response with videos and pagination metadata.
        """
        params: dict[str, Any] = {"region": region, "count": count, "cursor": cursor}
        response = await self._client.get(f"/v1/tiktok/hashtags/{name}/videos", params=params)
        return VideoListResponse.model_validate(response)
