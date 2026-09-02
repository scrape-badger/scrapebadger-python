"""Instagram Users API client.

Fetches user profiles and their content: posts, videos, reels, tagged/pinned
media, followers, following, stories, and highlights.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.instagram.models import (
    Highlight,
    Media,
    Paginated,
    User,
    UserAbout,
    UserShort,
)

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class UsersClient:
    """Client for Instagram user endpoints.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            profile = await client.instagram.users.get("instagram")
            print(f"@{profile.username}: {profile.follower_count:,} followers")

            posts = await client.instagram.users.posts("instagram", amount=12)
            for media in posts.items:
                print(media.code, media.like_count)
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        self._client = client

    async def get(self, username: str) -> User:
        """Get a user's full profile.

        Args:
            username: Instagram username (without the @ prefix).

        Returns:
            The :class:`User` profile.
        """
        response = await self._client.get(f"/v1/instagram/users/{username}")
        return User.model_validate(response)

    async def about(self, username: str) -> UserAbout:
        """Temporarily unavailable: authenticated Instagram data is temporarily offline.

        Get "About this account" metadata for a user.
        """
        response = await self._client.get(f"/v1/instagram/users/{username}/about")
        return UserAbout.model_validate(response)

    async def related(self, username: str) -> Paginated[UserShort]:
        """Temporarily unavailable: authenticated Instagram data is temporarily offline.

        Get accounts related/suggested for a user.
        """
        response = await self._client.get(f"/v1/instagram/users/{username}/related")
        return Paginated[UserShort].model_validate(response)

    async def posts(
        self,
        username: str,
        *,
        amount: int = 12,
        cursor: str | None = None,
    ) -> Paginated[Media]:
        """Get a user's timeline posts."""
        return await self._paginated_media(f"/v1/instagram/users/{username}/posts", amount, cursor)

    async def videos(
        self,
        username: str,
        *,
        amount: int = 12,
        cursor: str | None = None,
    ) -> Paginated[Media]:
        """Temporarily unavailable: authenticated Instagram data is temporarily offline.

        Get a user's video posts (IGTV/feed videos).
        """
        return await self._paginated_media(f"/v1/instagram/users/{username}/videos", amount, cursor)

    async def reels(
        self,
        username: str,
        *,
        amount: int = 12,
        cursor: str | None = None,
    ) -> Paginated[Media]:
        """Temporarily unavailable: authenticated Instagram data is temporarily offline.

        Get a user's reels.
        """
        return await self._paginated_media(f"/v1/instagram/users/{username}/reels", amount, cursor)

    async def tagged(
        self,
        username: str,
        *,
        amount: int = 12,
        cursor: str | None = None,
    ) -> Paginated[Media]:
        """Temporarily unavailable: authenticated Instagram data is temporarily offline.

        Get media a user is tagged in.
        """
        return await self._paginated_media(f"/v1/instagram/users/{username}/tagged", amount, cursor)

    async def pinned(self, username: str) -> Paginated[Media]:
        """Temporarily unavailable: authenticated Instagram data is temporarily offline.

        Get a user's pinned posts.
        """
        response = await self._client.get(f"/v1/instagram/users/{username}/pinned")
        return Paginated[Media].model_validate(response)

    async def followers(
        self,
        username: str,
        *,
        amount: int = 100,
        cursor: str | None = None,
        order: str | None = None,
    ) -> Paginated[UserShort]:
        """Temporarily unavailable: authenticated Instagram data is temporarily offline.

        Get a user's followers.

        Args:
            username: Instagram username.
            amount: Number of followers to return.
            cursor: Pagination cursor from a previous response.
            order: Ordering hint — e.g. ``"default"`` or ``"date_followed_earliest"``.
        """
        params: dict[str, Any] = {"amount": amount, "cursor": cursor, "order": order}
        response = await self._client.get(
            f"/v1/instagram/users/{username}/followers", params=params
        )
        return Paginated[UserShort].model_validate(response)

    async def following(
        self,
        username: str,
        *,
        amount: int = 100,
        cursor: str | None = None,
    ) -> Paginated[UserShort]:
        """Temporarily unavailable: authenticated Instagram data is temporarily offline.

        Get the accounts a user follows.
        """
        params: dict[str, Any] = {"amount": amount, "cursor": cursor}
        response = await self._client.get(
            f"/v1/instagram/users/{username}/following", params=params
        )
        return Paginated[UserShort].model_validate(response)

    async def search_followers(
        self,
        username: str,
        query: str,
        *,
        amount: int = 100,
        cursor: str | None = None,
    ) -> Paginated[UserShort]:
        """Temporarily unavailable: authenticated Instagram data is temporarily offline.

        Search within a user's followers by name/username.
        """
        params: dict[str, Any] = {"query": query, "amount": amount, "cursor": cursor}
        response = await self._client.get(
            f"/v1/instagram/users/{username}/followers/search", params=params
        )
        return Paginated[UserShort].model_validate(response)

    async def stories(self, username: str) -> Paginated[Media]:
        """Temporarily unavailable: authenticated Instagram data is temporarily offline.

        Get a user's currently-live stories.
        """
        response = await self._client.get(f"/v1/instagram/users/{username}/stories")
        return Paginated[Media].model_validate(response)

    async def highlights(self, username: str) -> Paginated[Highlight]:
        """Temporarily unavailable: authenticated Instagram data is temporarily offline.

        Get a user's story highlights.
        """
        response = await self._client.get(f"/v1/instagram/users/{username}/highlights")
        return Paginated[Highlight].model_validate(response)

    async def _paginated_media(
        self, path: str, amount: int, cursor: str | None
    ) -> Paginated[Media]:
        params: dict[str, Any] = {"amount": amount, "cursor": cursor}
        response = await self._client.get(path, params=params)
        return Paginated[Media].model_validate(response)
