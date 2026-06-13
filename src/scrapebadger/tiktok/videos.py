"""TikTok Videos API client.

Provides methods for video detail, comments, comment replies, related videos,
transcripts, and oEmbed metadata.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.tiktok.models import (
    CommentListResponse,
    TikTokOEmbed,
    TranscriptResponse,
    VideoListResponse,
    VideoResponse,
)

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class VideosClient:
    """Client for TikTok video endpoints (detail, comments, related, …).

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            detail = await client.tiktok.videos.get_detail("7212345678901234567")
            print(detail.video.description)

            comments = await client.tiktok.videos.get_comments("7212345678901234567")
            for c in comments.comments:
                print(c.text)
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize videos client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def get_detail(
        self,
        video_id: str,
        *,
        region: str = "US",
        username: str | None = None,
    ) -> VideoResponse:
        """Get full metadata for a single TikTok video/post.

        Args:
            video_id: The TikTok video/post id.
            region: Content region. Defaults to "US".
            username: Author handle. Passing it skips the oEmbed author lookup.

        Returns:
            Video response with the full video and the resolved region.

        Raises:
            NotFoundError: If the video doesn't exist.
            AuthenticationError: If the API key is invalid.

        Example:
            ```python
            detail = await client.tiktok.videos.get_detail("7212345678901234567")
            print(f"{detail.video.stats.play_count:,} views")
            ```
        """
        params: dict[str, Any] = {"region": region, "username": username}
        response = await self._client.get(f"/v1/tiktok/videos/{video_id}", params=params)
        return VideoResponse.model_validate(response)

    async def get_comments(
        self,
        video_id: str,
        *,
        region: str = "US",
        count: int = 20,
        cursor: str | None = None,
    ) -> CommentListResponse:
        """Get top-level comments on a TikTok video.

        Args:
            video_id: The TikTok video/post id.
            region: Content region. Defaults to "US".
            count: Number of comments to return (1-50). Defaults to 20.
            cursor: Pagination cursor from a prior response's pagination.cursor;
                omit for the first page.

        Returns:
            Comment list response with comments and pagination metadata.
        """
        params: dict[str, Any] = {"region": region, "count": count, "cursor": cursor}
        response = await self._client.get(f"/v1/tiktok/videos/{video_id}/comments", params=params)
        return CommentListResponse.model_validate(response)

    async def get_comment_replies(
        self,
        comment_id: str,
        *,
        video_id: str,
        region: str = "US",
        count: int = 20,
        cursor: str | None = None,
    ) -> CommentListResponse:
        """Get replies to a TikTok comment (best-effort).

        Args:
            comment_id: The parent comment id (cid).
            video_id: The parent video id.
            region: Content region. Defaults to "US".
            count: Number of replies to return (1-50). Defaults to 20.
            cursor: Pagination cursor from a prior response's pagination.cursor;
                omit for the first page.

        Returns:
            Comment list response with the reply comments and pagination metadata.
        """
        params: dict[str, Any] = {
            "video_id": video_id,
            "region": region,
            "count": count,
            "cursor": cursor,
        }
        response = await self._client.get(
            f"/v1/tiktok/comments/{comment_id}/replies", params=params
        )
        return CommentListResponse.model_validate(response)

    async def get_related(
        self,
        video_id: str,
        *,
        region: str = "US",
        count: int = 16,
    ) -> VideoListResponse:
        """Get TikTok's related videos for a given video.

        Args:
            video_id: The TikTok video/post id.
            region: Content region. Defaults to "US".
            count: Number of related videos to return (1-50). Defaults to 16.

        Returns:
            Video list response with related videos and pagination metadata.
        """
        params: dict[str, Any] = {"region": region, "count": count}
        response = await self._client.get(f"/v1/tiktok/videos/{video_id}/related", params=params)
        return VideoListResponse.model_validate(response)

    async def get_transcript(
        self,
        video_id: str,
        *,
        region: str = "US",
    ) -> TranscriptResponse:
        """Get subtitle/caption tracks for a TikTok video.

        Args:
            video_id: The TikTok video/post id.
            region: Content region. Defaults to "US".

        Returns:
            Transcript response with subtitle tracks and the voice-to-text string.
        """
        params: dict[str, Any] = {"region": region}
        response = await self._client.get(f"/v1/tiktok/videos/{video_id}/transcript", params=params)
        return TranscriptResponse.model_validate(response)

    async def get_oembed(
        self,
        url: str,
        *,
        region: str = "US",
    ) -> TikTokOEmbed:
        """Get cheap unauthenticated oEmbed metadata for a TikTok URL.

        Args:
            url: Full TikTok video or profile URL.
            region: Content region. Defaults to "US".

        Returns:
            oEmbed metadata for the URL.

        Example:
            ```python
            meta = await client.tiktok.videos.get_oembed(
                "https://www.tiktok.com/@charlidamelio/video/7212345678901234567",
            )
            print(meta.title)
            ```
        """
        params: dict[str, Any] = {"url": url, "region": region}
        response = await self._client.get("/v1/tiktok/oembed", params=params)
        return TikTokOEmbed.model_validate(response)
