"""YouTube Videos API client.

Provides methods for video detail, batch detail, related videos, streams, live
chat, oEmbed metadata, and single Shorts (detail + by-sound).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.youtube.models import (
    BatchResponse,
    ChannelTabResponse,
    LiveChatResponse,
    OEmbed,
    RelatedResponse,
    Short,
    StreamingData,
    Video,
)

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class VideosClient:
    """Client for YouTube video, short, stream, live-chat, and oEmbed endpoints.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            video = await client.youtube.videos.get_video("dQw4w9WgXcQ")
            print(video.title, video.view_count)

            related = await client.youtube.videos.get_related("dQw4w9WgXcQ")

            batch = await client.youtube.videos.batch(["id1", "id2"])
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize videos client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def get_video(
        self,
        video_id: str,
        *,
        gl: str | None = None,
        hl: str | None = None,
    ) -> Video:
        """Get a single video's full detail (merged ``player`` + ``next``).

        Args:
            video_id: The YouTube video id.
            gl: Content region (US, GB, DE…).
            hl: UI language.

        Returns:
            Full video detail including engagement, channel, chapters, and shelves.

        Raises:
            NotFoundError: If the video doesn't exist or is unavailable.
            AuthenticationError: If the API key is invalid.

        Example:
            ```python
            video = await client.youtube.videos.get_video("dQw4w9WgXcQ")
            print(f"{video.title}: {video.view_count:,} views")
            ```
        """
        params: dict[str, Any] = {"gl": gl, "hl": hl}
        response = await self._client.get(f"/v1/youtube/videos/{video_id}", params=params)
        return Video.model_validate(response)

    async def batch(
        self,
        video_ids: list[str],
        *,
        gl: str | None = None,
        hl: str | None = None,
    ) -> BatchResponse:
        """Fetch detail for up to 50 videos concurrently.

        Args:
            video_ids: A list of YouTube video ids (truncated to 50 server-side).
            gl: Content region (US, GB, DE…).
            hl: UI language.

        Returns:
            Batch response with parsed videos, per-id errors, and a success count.

        Example:
            ```python
            result = await client.youtube.videos.batch(["dQw4w9WgXcQ", "9bZkp7q19f0"])
            print(f"{result.count} ok, {len(result.errors)} failed")
            ```
        """
        payload: dict[str, Any] = {"video_ids": video_ids}
        if gl is not None:
            payload["gl"] = gl
        if hl is not None:
            payload["hl"] = hl
        response = await self._client.post("/v1/youtube/videos/batch", json=payload)
        return BatchResponse.model_validate(response)

    async def get_related(
        self,
        video_id: str,
        *,
        continuation: str | None = None,
        gl: str | None = None,
        hl: str | None = None,
    ) -> RelatedResponse:
        """Get videos related to a video (secondaryResults).

        Args:
            video_id: The YouTube video id.
            continuation: Pagination token from a previous page.
            gl: Content region (US, GB, DE…).
            hl: UI language.

        Returns:
            Related response with result cards and a continuation token.

        Example:
            ```python
            related = await client.youtube.videos.get_related("dQw4w9WgXcQ")
            ```
        """
        params: dict[str, Any] = {"continuation": continuation, "gl": gl, "hl": hl}
        response = await self._client.get(f"/v1/youtube/videos/{video_id}/related", params=params)
        return RelatedResponse.model_validate(response)

    async def get_streams(
        self,
        video_id: str,
        *,
        gl: str | None = None,
        client: str = "IOS",
    ) -> StreamingData:
        """Get stream/format metadata for a video (best-effort URLs).

        Args:
            video_id: The YouTube video id.
            gl: Content region (US, GB, DE…).
            client: InnerTube client context ("IOS", "ANDROID", "WEB"). Defaults to "IOS".

        Returns:
            Streaming data with muxed and adaptive formats. Media URLs may be
            PO-token gated and are therefore best-effort.

        Example:
            ```python
            streams = await client.youtube.videos.get_streams("dQw4w9WgXcQ")
            for fmt in streams.adaptive_formats:
                print(fmt.itag, fmt.quality_label)
            ```
        """
        params: dict[str, Any] = {"gl": gl, "client": client}
        response = await self._client.get(f"/v1/youtube/videos/{video_id}/streams", params=params)
        return StreamingData.model_validate(response)

    async def get_live_chat(
        self,
        video_id: str,
        *,
        continuation: str | None = None,
        replay: bool = False,
        gl: str | None = None,
        hl: str | None = None,
    ) -> LiveChatResponse:
        """Get live-chat (or chat-replay) messages for a stream.

        Args:
            video_id: The YouTube video id.
            continuation: Pagination token from a previous page.
            replay: Fetch chat replay for a finished stream. Defaults to False.
            gl: Content region (US, GB, DE…).
            hl: UI language.

        Returns:
            Live chat response with messages and a continuation token.

        Example:
            ```python
            chat = await client.youtube.videos.get_live_chat("liveVideoId")
            for m in chat.messages:
                print(f"{m.author}: {m.text}")
            ```
        """
        params: dict[str, Any] = {
            "continuation": continuation,
            "replay": replay,
            "gl": gl,
            "hl": hl,
        }
        response = await self._client.get(f"/v1/youtube/videos/{video_id}/live_chat", params=params)
        return LiveChatResponse.model_validate(response)

    async def oembed(self, url: str) -> OEmbed:
        """Get public oEmbed metadata for a YouTube URL.

        Args:
            url: A YouTube video/playlist/channel URL.

        Returns:
            oEmbed response with title, author, thumbnail, and embed HTML.

        Example:
            ```python
            meta = await client.youtube.videos.oembed(
                "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            )
            print(meta.title, meta.author_name)
            ```
        """
        params: dict[str, Any] = {"url": url}
        response = await self._client.get("/v1/youtube/oembed", params=params)
        return OEmbed.model_validate(response)

    async def get_short(
        self,
        video_id: str,
        *,
        gl: str | None = None,
        hl: str | None = None,
    ) -> Short:
        """Get a single Short's detail.

        Args:
            video_id: The Shorts video id.
            gl: Content region (US, GB, DE…).
            hl: UI language.

        Returns:
            Short detail (a Video subtype with ``is_short=True``).

        Raises:
            NotFoundError: If the short doesn't exist or is unavailable.

        Example:
            ```python
            short = await client.youtube.videos.get_short("shortVideoId")
            ```
        """
        params: dict[str, Any] = {"gl": gl, "hl": hl}
        response = await self._client.get(f"/v1/youtube/shorts/{video_id}", params=params)
        return Short.model_validate(response)

    async def shorts_by_sound(
        self,
        sound_id: str,
        *,
        continuation: str | None = None,
        gl: str | None = None,
        hl: str | None = None,
    ) -> ChannelTabResponse:
        """List Shorts attributed to a given sound/music id (best-effort).

        Args:
            sound_id: The sound/music id.
            continuation: Pagination token from a previous page.
            gl: Content region (US, GB, DE…).
            hl: UI language.

        Returns:
            A tab response with Shorts items and a continuation token.

        Example:
            ```python
            result = await client.youtube.videos.shorts_by_sound("soundId")
            ```
        """
        params: dict[str, Any] = {"continuation": continuation, "gl": gl, "hl": hl}
        response = await self._client.get(f"/v1/youtube/shorts/by_sound/{sound_id}", params=params)
        return ChannelTabResponse.model_validate(response)
