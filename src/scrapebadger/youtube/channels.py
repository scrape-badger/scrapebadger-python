"""YouTube Channels API client.

Provides methods for channel detail, handle/URL resolution, the channel tabs
(videos, shorts, streams, playlists, community), about, subscriber count, and
in-channel search.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.youtube.models import (
    Channel,
    ChannelAbout,
    ChannelTabResponse,
    CommunityPost,
    CommunityResponse,
    ResolveResult,
    SearchResponse,
    SubscriberCount,
)

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class ChannelsClient:
    """Client for YouTube channel endpoints (detail, tabs, about, search, resolve).

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            channel = await client.youtube.channels.get_channel("@mkbhd")
            print(channel.title, channel.number_of_subscribers)

            videos = await client.youtube.channels.get_videos("@mkbhd")
            for v in videos.items:
                print(v.title)
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize channels client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def get_channel(
        self,
        channel_id: str,
        *,
        gl: str | None = None,
        hl: str | None = None,
    ) -> Channel:
        """Get a channel's full detail.

        Args:
            channel_id: A UC id, @handle, or custom URL.
            gl: Content region (US, GB, DE…).
            hl: UI language.

        Returns:
            Full channel detail including subscribers, banners, links, and tabs.

        Raises:
            NotFoundError: If the channel doesn't exist.
            AuthenticationError: If the API key is invalid.

        Example:
            ```python
            channel = await client.youtube.channels.get_channel("@mkbhd")
            ```
        """
        params: dict[str, Any] = {"gl": gl, "hl": hl}
        response = await self._client.get(f"/v1/youtube/channels/{channel_id}", params=params)
        return Channel.model_validate(response)

    async def resolve(
        self,
        *,
        handle: str | None = None,
        url: str | None = None,
        gl: str | None = None,
        hl: str | None = None,
    ) -> ResolveResult:
        """Resolve a handle or URL to canonical channel/video/playlist ids.

        Args:
            handle: A @handle or custom name.
            url: A full channel/video/playlist URL.
            gl: Content region (US, GB, DE…).
            hl: UI language.

        Returns:
            Resolve result with the canonical ids and URL.

        Example:
            ```python
            result = await client.youtube.channels.resolve(handle="@mkbhd")
            print(result.channel_id)
            ```
        """
        params: dict[str, Any] = {"handle": handle, "url": url, "gl": gl, "hl": hl}
        response = await self._client.get("/v1/youtube/channels/resolve", params=params)
        return ResolveResult.model_validate(response)

    async def get_videos(
        self,
        channel_id: str,
        *,
        continuation: str | None = None,
        gl: str | None = None,
        hl: str | None = None,
    ) -> ChannelTabResponse:
        """List a channel's videos.

        Args:
            channel_id: A UC id, @handle, or custom URL.
            continuation: Pagination token from a previous page.
            gl: Content region (US, GB, DE…).
            hl: UI language.

        Returns:
            A tab response with video items and a continuation token.

        Example:
            ```python
            videos = await client.youtube.channels.get_videos("@mkbhd")
            ```
        """
        params: dict[str, Any] = {"continuation": continuation, "gl": gl, "hl": hl}
        response = await self._client.get(
            f"/v1/youtube/channels/{channel_id}/videos", params=params
        )
        return ChannelTabResponse.model_validate(response)

    async def get_shorts(
        self,
        channel_id: str,
        *,
        continuation: str | None = None,
        gl: str | None = None,
        hl: str | None = None,
    ) -> ChannelTabResponse:
        """List a channel's Shorts.

        Args:
            channel_id: A UC id, @handle, or custom URL.
            continuation: Pagination token from a previous page.
            gl: Content region (US, GB, DE…).
            hl: UI language.

        Returns:
            A tab response with Shorts items and a continuation token.

        Example:
            ```python
            shorts = await client.youtube.channels.get_shorts("@mkbhd")
            ```
        """
        params: dict[str, Any] = {"continuation": continuation, "gl": gl, "hl": hl}
        response = await self._client.get(
            f"/v1/youtube/channels/{channel_id}/shorts", params=params
        )
        return ChannelTabResponse.model_validate(response)

    async def get_streams(
        self,
        channel_id: str,
        *,
        continuation: str | None = None,
        gl: str | None = None,
        hl: str | None = None,
    ) -> ChannelTabResponse:
        """List a channel's live streams.

        Args:
            channel_id: A UC id, @handle, or custom URL.
            continuation: Pagination token from a previous page.
            gl: Content region (US, GB, DE…).
            hl: UI language.

        Returns:
            A tab response with stream items and a continuation token.

        Example:
            ```python
            streams = await client.youtube.channels.get_streams("@mkbhd")
            ```
        """
        params: dict[str, Any] = {"continuation": continuation, "gl": gl, "hl": hl}
        response = await self._client.get(
            f"/v1/youtube/channels/{channel_id}/streams", params=params
        )
        return ChannelTabResponse.model_validate(response)

    async def get_playlists(
        self,
        channel_id: str,
        *,
        continuation: str | None = None,
        gl: str | None = None,
        hl: str | None = None,
    ) -> ChannelTabResponse:
        """List a channel's playlists.

        Args:
            channel_id: A UC id, @handle, or custom URL.
            continuation: Pagination token from a previous page.
            gl: Content region (US, GB, DE…).
            hl: UI language.

        Returns:
            A tab response with playlist items and a continuation token.

        Example:
            ```python
            playlists = await client.youtube.channels.get_playlists("@mkbhd")
            ```
        """
        params: dict[str, Any] = {"continuation": continuation, "gl": gl, "hl": hl}
        response = await self._client.get(
            f"/v1/youtube/channels/{channel_id}/playlists", params=params
        )
        return ChannelTabResponse.model_validate(response)

    async def get_community(
        self,
        channel_id: str,
        *,
        continuation: str | None = None,
        gl: str | None = None,
        hl: str | None = None,
    ) -> CommunityResponse:
        """List a channel's community posts.

        Args:
            channel_id: A UC id, @handle, or custom URL.
            continuation: Pagination token from a previous page.
            gl: Content region (US, GB, DE…).
            hl: UI language.

        Returns:
            Community response with posts and a continuation token.

        Example:
            ```python
            community = await client.youtube.channels.get_community("@mkbhd")
            ```
        """
        params: dict[str, Any] = {"continuation": continuation, "gl": gl, "hl": hl}
        response = await self._client.get(
            f"/v1/youtube/channels/{channel_id}/community", params=params
        )
        return CommunityResponse.model_validate(response)

    async def get_about(
        self,
        channel_id: str,
        *,
        gl: str | None = None,
        hl: str | None = None,
    ) -> ChannelAbout:
        """Get a channel's lightweight about payload.

        Args:
            channel_id: A UC id, @handle, or custom URL.
            gl: Content region (US, GB, DE…).
            hl: UI language.

        Returns:
            Channel about with description, links, totals, and join date.

        Example:
            ```python
            about = await client.youtube.channels.get_about("@mkbhd")
            ```
        """
        params: dict[str, Any] = {"gl": gl, "hl": hl}
        response = await self._client.get(f"/v1/youtube/channels/{channel_id}/about", params=params)
        return ChannelAbout.model_validate(response)

    async def get_subscriber_count(
        self,
        channel_id: str,
        *,
        gl: str | None = None,
        hl: str | None = None,
    ) -> SubscriberCount:
        """Get a channel's subscriber count (fast path).

        Args:
            channel_id: A UC id, @handle, or custom URL.
            gl: Content region (US, GB, DE…).
            hl: UI language.

        Returns:
            Subscriber count response.

        Example:
            ```python
            subs = await client.youtube.channels.get_subscriber_count("@mkbhd")
            print(subs.number_of_subscribers)
            ```
        """
        params: dict[str, Any] = {"gl": gl, "hl": hl}
        response = await self._client.get(
            f"/v1/youtube/channels/{channel_id}/subscriber_count", params=params
        )
        return SubscriberCount.model_validate(response)

    async def search(
        self,
        channel_id: str,
        query: str,
        *,
        continuation: str | None = None,
        gl: str | None = None,
        hl: str | None = None,
    ) -> SearchResponse:
        """Search within a single channel.

        Args:
            channel_id: A UC id, @handle, or custom URL.
            query: Search keywords.
            continuation: Pagination token from a previous page.
            gl: Content region (US, GB, DE…).
            hl: UI language.

        Returns:
            Search response with matching results and a continuation token.

        Example:
            ```python
            results = await client.youtube.channels.search("@mkbhd", "iphone")
            ```
        """
        params: dict[str, Any] = {
            "query": query,
            "continuation": continuation,
            "gl": gl,
            "hl": hl,
        }
        response = await self._client.get(
            f"/v1/youtube/channels/{channel_id}/search", params=params
        )
        return SearchResponse.model_validate(response)

    async def get_post(
        self,
        post_id: str,
        *,
        gl: str | None = None,
        hl: str | None = None,
    ) -> CommunityPost:
        """Get a single community post's detail.

        Args:
            post_id: The community post id.
            gl: Content region (US, GB, DE…).
            hl: UI language.

        Returns:
            Community post detail (text, poll, images, or attached video/shared post).

        Raises:
            NotFoundError: If the post doesn't exist.

        Example:
            ```python
            post = await client.youtube.channels.get_post("postId")
            ```
        """
        params: dict[str, Any] = {"gl": gl, "hl": hl}
        response = await self._client.get(f"/v1/youtube/posts/{post_id}", params=params)
        return CommunityPost.model_validate(response)
