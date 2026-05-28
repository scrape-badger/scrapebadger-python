"""Reddit Users API client.

Provides methods for fetching user profiles, their posts, comments,
moderated subreddits, and trophies.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.reddit.models import (
    UserCommentsResponse,
    UserModeratedResponse,
    UserPostsResponse,
    UserProfileResponse,
    UserTrophiesResponse,
)

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class UsersClient:
    """Client for Reddit user endpoints.

    Provides async methods for fetching user profiles and activity.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            # Get user profile
            result = await client.reddit.users.get("spez")
            user = result.user
            print(f"u/{user.name}: {user.total_karma:,} karma")

            # Get user's posts
            posts = await client.reddit.users.posts("spez", sort="top")
            for post in posts.posts:
                print(f"  r/{post.subreddit}: {post.title}")

            # Get trophies
            trophies = await client.reddit.users.trophies("spez")
            for trophy in trophies.trophies:
                print(f"  {trophy.name}")
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize users client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def get(self, username: str) -> UserProfileResponse:
        """Get a Reddit user's profile.

        Args:
            username: Reddit username (without u/ prefix).

        Returns:
            UserProfileResponse with full user profile data.

        Raises:
            NotFoundError: If the user doesn't exist or is suspended.
            AuthenticationError: If the API key is invalid.

        Example:
            ```python
            result = await client.reddit.users.get("spez")
            user = result.user
            print(f"u/{user.name}")
            print(f"Post karma: {user.link_karma:,}")
            print(f"Comment karma: {user.comment_karma:,}")
            print(f"Account age: {user.created_utc}")
            ```
        """
        response = await self._client.get(f"/v1/reddit/users/{username}")
        return UserProfileResponse.model_validate(response)

    async def posts(
        self,
        username: str,
        *,
        sort: str = "new",
        time_filter: str | None = None,
        limit: int = 25,
        after: str | None = None,
    ) -> UserPostsResponse:
        """Get posts submitted by a Reddit user.

        Args:
            username: Reddit username (without u/ prefix).
            sort: Sort order — "new", "hot", "top", "controversial".
                Defaults to "new".
            time_filter: Time window for "top"/"controversial" sort —
                "hour", "day", "week", "month", "year", "all". Optional.
            limit: Number of posts (1-100). Defaults to 25.
            after: Pagination cursor from a previous response.

        Returns:
            UserPostsResponse with the user's submitted posts.

        Raises:
            NotFoundError: If the user doesn't exist.
            AuthenticationError: If the API key is invalid.

        Example:
            ```python
            result = await client.reddit.users.posts(
                "spez",
                sort="top",
                time_filter="year",
                limit=10,
            )
            for post in result.posts:
                print(f"r/{post.subreddit}: {post.title} ({post.score} pts)")
            ```
        """
        params: dict[str, Any] = {
            "sort": sort,
            "t": time_filter,
            "limit": limit,
            "after": after,
        }
        response = await self._client.get(
            f"/v1/reddit/users/{username}/posts",
            params=params,
        )
        return UserPostsResponse.model_validate(response)

    async def comments(
        self,
        username: str,
        *,
        sort: str = "new",
        time_filter: str | None = None,
        limit: int = 25,
        after: str | None = None,
    ) -> UserCommentsResponse:
        """Get comments made by a Reddit user.

        Args:
            username: Reddit username (without u/ prefix).
            sort: Sort order — "new", "hot", "top", "controversial".
                Defaults to "new".
            time_filter: Time window for "top"/"controversial" sort —
                "hour", "day", "week", "month", "year", "all". Optional.
            limit: Number of comments (1-100). Defaults to 25.
            after: Pagination cursor from a previous response.

        Returns:
            UserCommentsResponse with the user's comments.

        Raises:
            NotFoundError: If the user doesn't exist.
            AuthenticationError: If the API key is invalid.

        Example:
            ```python
            result = await client.reddit.users.comments("spez", limit=50)
            for comment in result.comments:
                print(f"r/{comment.subreddit}: {comment.body[:80]}")
            ```
        """
        params: dict[str, Any] = {
            "sort": sort,
            "t": time_filter,
            "limit": limit,
            "after": after,
        }
        response = await self._client.get(
            f"/v1/reddit/users/{username}/comments",
            params=params,
        )
        return UserCommentsResponse.model_validate(response)

    async def moderated(self, username: str) -> UserModeratedResponse:
        """Get the list of subreddits moderated by a user.

        Args:
            username: Reddit username (without u/ prefix).

        Returns:
            UserModeratedResponse with moderated subreddits.

        Raises:
            NotFoundError: If the user doesn't exist.
            AuthenticationError: If the API key is invalid.

        Example:
            ```python
            result = await client.reddit.users.moderated("spez")
            for sub in result.subreddits:
                print(f"r/{sub.name}: {sub.subscribers:,} members")
            ```
        """
        response = await self._client.get(f"/v1/reddit/users/{username}/moderated")
        return UserModeratedResponse.model_validate(response)

    async def trophies(self, username: str) -> UserTrophiesResponse:
        """Get the trophies/awards earned by a Reddit user.

        Args:
            username: Reddit username (without u/ prefix).

        Returns:
            UserTrophiesResponse with the user's trophies.

        Raises:
            NotFoundError: If the user doesn't exist.
            AuthenticationError: If the API key is invalid.

        Example:
            ```python
            result = await client.reddit.users.trophies("spez")
            for trophy in result.trophies:
                print(f"  {trophy.name}: {trophy.description}")
            ```
        """
        response = await self._client.get(f"/v1/reddit/users/{username}/trophies")
        return UserTrophiesResponse.model_validate(response)
