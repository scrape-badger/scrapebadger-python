"""TikTok Users API client.

Provides methods for user profile, videos, followers, following, liked, and
reposted videos.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.tiktok.models import (
    ProfileResponse,
    UserListResponse,
    VideoListResponse,
)

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class UsersClient:
    """Client for TikTok user endpoints (profile, videos, followers, …).

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            profile = await client.tiktok.users.get_profile("charlidamelio")
            print(profile.user.nickname)

            videos = await client.tiktok.users.get_videos("charlidamelio")
            for v in videos.videos:
                print(v.description)
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize users client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def get_profile(
        self,
        username: str,
        *,
        region: str = "US",
    ) -> ProfileResponse:
        """Get a TikTok user's full profile.

        Args:
            username: The TikTok @handle (without the leading '@').
            region: Content region (ISO 3166-1 alpha-2). Defaults to "US".

        Returns:
            Profile response with the user and the resolved region.

        Raises:
            NotFoundError: If the user doesn't exist.
            AuthenticationError: If the API key is invalid.

        Example:
            ```python
            profile = await client.tiktok.users.get_profile("charlidamelio")
            print(f"{profile.user.nickname}: {profile.user.stats.follower_count:,}")
            ```
        """
        params: dict[str, Any] = {"region": region}
        response = await self._client.get(f"/v1/tiktok/users/{username}", params=params)
        return ProfileResponse.model_validate(response)

    async def get_videos(
        self,
        username: str,
        *,
        region: str = "US",
        count: int = 30,
        cursor: str | None = None,
    ) -> VideoListResponse:
        """Get a TikTok user's posted videos.

        Args:
            username: The TikTok @handle.
            region: Content region. Defaults to "US".
            count: Number of videos to return (1-50). Defaults to 30.
            cursor: Opaque pagination cursor from a previous page.

        Returns:
            Video list response with videos and pagination metadata.

        Example:
            ```python
            page = await client.tiktok.users.get_videos("charlidamelio", count=50)
            if page.pagination.has_more:
                more = await client.tiktok.users.get_videos(
                    "charlidamelio", cursor=page.pagination.cursor,
                )
            ```
        """
        params: dict[str, Any] = {"region": region, "count": count, "cursor": cursor}
        response = await self._client.get(f"/v1/tiktok/users/{username}/videos", params=params)
        return VideoListResponse.model_validate(response)

    async def get_followers(
        self,
        username: str,
        *,
        region: str = "US",
        count: int = 30,
    ) -> UserListResponse:
        """Get a TikTok user's followers (best-effort; often guest-gated).

        Args:
            username: The TikTok @handle.
            region: Content region. Defaults to "US".
            count: Number of followers to return (1-50). Defaults to 30.

        Returns:
            User list response with author summaries and pagination metadata.
        """
        params: dict[str, Any] = {"region": region, "count": count}
        response = await self._client.get(f"/v1/tiktok/users/{username}/followers", params=params)
        return UserListResponse.model_validate(response)

    async def get_following(
        self,
        username: str,
        *,
        region: str = "US",
        count: int = 30,
    ) -> UserListResponse:
        """Get accounts a TikTok user follows (best-effort).

        Args:
            username: The TikTok @handle.
            region: Content region. Defaults to "US".
            count: Number of accounts to return (1-50). Defaults to 30.

        Returns:
            User list response with author summaries and pagination metadata.
        """
        params: dict[str, Any] = {"region": region, "count": count}
        response = await self._client.get(f"/v1/tiktok/users/{username}/following", params=params)
        return UserListResponse.model_validate(response)

    async def get_liked(
        self,
        username: str,
        *,
        region: str = "US",
        count: int = 30,
    ) -> VideoListResponse:
        """Get a TikTok user's liked videos (only if their Liked tab is public).

        Args:
            username: The TikTok @handle.
            region: Content region. Defaults to "US".
            count: Number of videos to return (1-50). Defaults to 30.

        Returns:
            Video list response with videos and pagination metadata.
        """
        params: dict[str, Any] = {"region": region, "count": count}
        response = await self._client.get(f"/v1/tiktok/users/{username}/liked", params=params)
        return VideoListResponse.model_validate(response)

    async def get_reposts(
        self,
        username: str,
        *,
        region: str = "US",
        count: int = 30,
    ) -> VideoListResponse:
        """Get videos a TikTok user has reposted.

        Args:
            username: The TikTok @handle.
            region: Content region. Defaults to "US".
            count: Number of videos to return (1-50). Defaults to 30.

        Returns:
            Video list response with videos and pagination metadata.
        """
        params: dict[str, Any] = {"region": region, "count": count}
        response = await self._client.get(f"/v1/tiktok/users/{username}/reposts", params=params)
        return VideoListResponse.model_validate(response)
