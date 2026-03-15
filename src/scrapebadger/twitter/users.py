"""Twitter Users API client.

Provides methods for fetching user profiles, followers, following, and related data.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from scrapebadger._internal.pagination import PaginatedResponse, paginate
from scrapebadger.twitter.models import Tweet, User, UserAbout, UserIds

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from scrapebadger._internal.client import BaseClient


class UsersClient:
    """Client for Twitter users endpoints.

    Provides async methods for fetching user profiles, followers, following,
    and other user-related data.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            # Get user profile
            user = await client.twitter.users.get_by_username("elonmusk")
            print(f"{user.name}: {user.followers_count:,} followers")

            # Get followers
            followers = await client.twitter.users.get_followers("elonmusk")

            # Iterate through all followers
            async for follower in client.twitter.users.get_followers_all("elonmusk"):
                print(follower.username)
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize users client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def get_by_id(self, user_id: str) -> User:
        """Get a user by their numeric ID.

        Args:
            user_id: The user's numeric ID.

        Returns:
            The user profile.

        Raises:
            NotFoundError: If the user doesn't exist.

        Example:
            ```python
            user = await client.twitter.users.get_by_id("44196397")
            print(f"@{user.username}")
            ```
        """
        response = await self._client.get(f"/v1/twitter/users/{user_id}/by_id")
        return User.model_validate(response)

    async def get_by_username(self, username: str) -> User:
        """Get a user by their username.

        Args:
            username: The user's username (without @).

        Returns:
            The user profile.

        Raises:
            NotFoundError: If the user doesn't exist.

        Example:
            ```python
            user = await client.twitter.users.get_by_username("elonmusk")
            print(f"{user.name} has {user.followers_count:,} followers")
            ```
        """
        response = await self._client.get(f"/v1/twitter/users/{username}/by_username")
        return User.model_validate(response)

    async def get_about(self, username: str) -> UserAbout:
        """Get extended "About" information for a user.

        Returns additional metadata including account location,
        username change history, and verification details.

        Args:
            username: The user's username (without @).

        Returns:
            Extended user information.

        Example:
            ```python
            about = await client.twitter.users.get_about("elonmusk")
            print(f"Account based in: {about.account_based_in}")
            print(f"Username changes: {about.username_changes}")
            ```
        """
        response = await self._client.get(f"/v1/twitter/users/{username}/about")
        return UserAbout.model_validate(response)

    async def get_followers(
        self,
        username: str,
        *,
        cursor: str | None = None,
    ) -> PaginatedResponse[User]:
        """Get a user's followers.

        Args:
            username: The user's username (without @).
            cursor: Pagination cursor for fetching more results.

        Returns:
            Paginated response containing follower users.

        Example:
            ```python
            followers = await client.twitter.users.get_followers("elonmusk")
            for user in followers.data:
                print(f"@{user.username}")

            # Get next page
            if followers.has_more:
                more = await client.twitter.users.get_followers(
                    "elonmusk",
                    cursor=followers.next_cursor
                )
            ```
        """
        response = await self._client.get(
            f"/v1/twitter/users/{username}/followers",
            params={"cursor": cursor},
        )
        data = [User.model_validate(item) for item in response.get("data", []) or []]
        return PaginatedResponse(data=data, next_cursor=response.get("next_cursor"))

    async def get_followers_all(
        self,
        username: str,
        *,
        max_pages: int | None = None,
        max_items: int | None = None,
    ) -> AsyncIterator[User]:
        """Iterate through all followers with automatic pagination.

        Args:
            username: The user's username (without @).
            max_pages: Maximum number of pages to fetch.
            max_items: Maximum number of users to yield.

        Yields:
            User objects for each follower.

        Example:
            ```python
            async for follower in client.twitter.users.get_followers_all(
                "elonmusk",
                max_items=1000
            ):
                print(follower.username)
            ```
        """
        async for user in paginate(
            self._client,
            f"/v1/twitter/users/{username}/followers",
            {},
            User.model_validate,
            max_pages=max_pages,
            max_items=max_items,
        ):
            yield user

    async def get_following(
        self,
        username: str,
        *,
        cursor: str | None = None,
    ) -> PaginatedResponse[User]:
        """Get users that a user is following.

        Args:
            username: The user's username (without @).
            cursor: Pagination cursor for fetching more results.

        Returns:
            Paginated response containing followed users.

        Example:
            ```python
            following = await client.twitter.users.get_following("elonmusk")
            for user in following.data:
                print(f"Follows @{user.username}")
            ```
        """
        response = await self._client.get(
            f"/v1/twitter/users/{username}/followings",
            params={"cursor": cursor},
        )
        data = [User.model_validate(item) for item in response.get("data", []) or []]
        return PaginatedResponse(data=data, next_cursor=response.get("next_cursor"))

    async def get_following_all(
        self,
        username: str,
        *,
        max_pages: int | None = None,
        max_items: int | None = None,
    ) -> AsyncIterator[User]:
        """Iterate through all following with automatic pagination.

        Args:
            username: The user's username (without @).
            max_pages: Maximum number of pages to fetch.
            max_items: Maximum number of users to yield.

        Yields:
            User objects for each followed account.
        """
        async for user in paginate(
            self._client,
            f"/v1/twitter/users/{username}/followings",
            {},
            User.model_validate,
            max_pages=max_pages,
            max_items=max_items,
        ):
            yield user

    async def get_latest_followers(
        self,
        username: str,
        *,
        count: int = 200,
        cursor: str | None = None,
    ) -> PaginatedResponse[User]:
        """Get a user's most recent followers.

        Args:
            username: The user's username (without @).
            count: Number of followers per page (max 200).
            cursor: Pagination cursor for fetching more results.

        Returns:
            Paginated response containing recent followers.
        """
        response = await self._client.get(
            f"/v1/twitter/users/{username}/latest_followers",
            params={"count": count, "cursor": cursor},
        )
        data = [User.model_validate(item) for item in response.get("data", []) or []]
        return PaginatedResponse(data=data, next_cursor=response.get("next_cursor"))

    async def get_latest_following(
        self,
        username: str,
        *,
        count: int = 200,
        cursor: str | None = None,
    ) -> PaginatedResponse[User]:
        """Get accounts a user most recently followed.

        Args:
            username: The user's username (without @).
            count: Number of users per page (max 200).
            cursor: Pagination cursor for fetching more results.

        Returns:
            Paginated response containing recently followed users.
        """
        response = await self._client.get(
            f"/v1/twitter/users/{username}/latest_following",
            params={"count": count, "cursor": cursor},
        )
        data = [User.model_validate(item) for item in response.get("data", []) or []]
        return PaginatedResponse(data=data, next_cursor=response.get("next_cursor"))

    async def get_follower_ids(
        self,
        username: str,
        *,
        count: int = 5000,
        cursor: str | None = None,
    ) -> UserIds:
        """Get follower IDs for a user.

        More efficient than get_followers when you only need IDs.

        Args:
            username: The user's username (without @).
            count: Number of IDs per page (max 5000).
            cursor: Pagination cursor for fetching more results.

        Returns:
            UserIds containing list of follower IDs.

        Example:
            ```python
            ids = await client.twitter.users.get_follower_ids("elonmusk")
            print(f"Found {len(ids.ids):,} follower IDs")
            ```
        """
        response = await self._client.get(
            f"/v1/twitter/users/{username}/follower_ids",
            params={"count": count, "cursor": cursor},
        )
        data = response.get("data", {}) or {}
        return UserIds(
            ids=data.get("ids", []),
            next_cursor=data.get("next_cursor"),
        )

    async def get_following_ids(
        self,
        username: str,
        *,
        count: int = 5000,
        cursor: str | None = None,
    ) -> UserIds:
        """Get following IDs for a user.

        More efficient than get_following when you only need IDs.

        Args:
            username: The user's username (without @).
            count: Number of IDs per page (max 5000).
            cursor: Pagination cursor for fetching more results.

        Returns:
            UserIds containing list of following IDs.
        """
        response = await self._client.get(
            f"/v1/twitter/users/{username}/following_ids",
            params={"count": count, "cursor": cursor},
        )
        data = response.get("data", {}) or {}
        return UserIds(
            ids=data.get("ids", []),
            next_cursor=data.get("next_cursor"),
        )

    async def get_verified_followers(
        self,
        user_id: str,
        *,
        count: int = 20,
        cursor: str | None = None,
    ) -> PaginatedResponse[User]:
        """Get verified followers for a user.

        Args:
            user_id: The user's numeric ID.
            count: Number of users per page.
            cursor: Pagination cursor for fetching more results.

        Returns:
            Paginated response containing verified followers.
        """
        response = await self._client.get(
            f"/v1/twitter/users/{user_id}/verified_followers",
            params={"count": count, "cursor": cursor},
        )
        data = [User.model_validate(item) for item in response.get("data", []) or []]
        return PaginatedResponse(data=data, next_cursor=response.get("next_cursor"))

    async def get_followers_you_know(
        self,
        user_id: str,
        *,
        count: int = 20,
        cursor: str | None = None,
    ) -> PaginatedResponse[User]:
        """Get followers that the authenticated user also follows.

        Args:
            user_id: The user's numeric ID.
            count: Number of users per page.
            cursor: Pagination cursor for fetching more results.

        Returns:
            Paginated response containing mutual connections.
        """
        response = await self._client.get(
            f"/v1/twitter/users/{user_id}/followers_you_know",
            params={"count": count, "cursor": cursor},
        )
        data = [User.model_validate(item) for item in response.get("data", []) or []]
        return PaginatedResponse(data=data, next_cursor=response.get("next_cursor"))

    async def get_subscriptions(
        self,
        user_id: str,
        *,
        count: int = 20,
        cursor: str | None = None,
    ) -> PaginatedResponse[User]:
        """Get premium accounts that a user subscribes to.

        Args:
            user_id: The user's numeric ID.
            count: Number of users per page.
            cursor: Pagination cursor for fetching more results.

        Returns:
            Paginated response containing subscribed accounts.
        """
        response = await self._client.get(
            f"/v1/twitter/users/{user_id}/subscriptions",
            params={"count": count, "cursor": cursor},
        )
        data = [User.model_validate(item) for item in response.get("data", []) or []]
        return PaginatedResponse(data=data, next_cursor=response.get("next_cursor"))

    async def get_highlights(
        self,
        user_id: str,
        *,
        count: int = 20,
        cursor: str | None = None,
    ) -> PaginatedResponse[Tweet]:
        """Get a user's highlighted tweets.

        Args:
            user_id: The user's numeric ID.
            count: Number of tweets per page.
            cursor: Pagination cursor for fetching more results.

        Returns:
            Paginated response containing highlighted tweets.
        """
        response = await self._client.get(
            f"/v1/twitter/users/{user_id}/highlights",
            params={"count": count, "cursor": cursor},
        )
        data = [Tweet.model_validate(item) for item in response.get("data", []) or []]
        return PaginatedResponse(data=data, next_cursor=response.get("next_cursor"))

    async def search(
        self,
        query: str,
        *,
        cursor: str | None = None,
    ) -> PaginatedResponse[User]:
        """Search for users.

        Args:
            query: Search query string.
            cursor: Pagination cursor for fetching more results.

        Returns:
            Paginated response containing matching users.

        Example:
            ```python
            results = await client.twitter.users.search("python developer")
            for user in results.data:
                print(f"@{user.username}: {user.description}")
            ```
        """
        response = await self._client.get(
            "/v1/twitter/users/search_users",
            params={"query": query, "cursor": cursor},
        )
        data = [User.model_validate(item) for item in response.get("data", []) or []]
        return PaginatedResponse(data=data, next_cursor=response.get("next_cursor"))

    async def search_all(
        self,
        query: str,
        *,
        max_pages: int | None = None,
        max_items: int | None = None,
    ) -> AsyncIterator[User]:
        """Iterate through all search results with automatic pagination.

        Args:
            query: Search query string.
            max_pages: Maximum number of pages to fetch.
            max_items: Maximum number of users to yield.

        Yields:
            User objects matching the search query.
        """
        async for user in paginate(
            self._client,
            "/v1/twitter/users/search_users",
            {"query": query},
            User.model_validate,
            max_pages=max_pages,
            max_items=max_items,
        ):
            yield user

    async def get_by_ids(self, user_ids: list[str]) -> PaginatedResponse[User]:
        """Get multiple users by their numeric IDs.

        Args:
            user_ids: List of numeric user IDs to fetch.

        Returns:
            Paginated response containing the users.

        Example:
            ```python
            users = await client.twitter.users.get_by_ids(["44196397", "783214"])
            for user in users.data:
                print(f"@{user.username}")
            ```
        """
        ids_param = ",".join(user_ids)
        response = await self._client.get("/v1/twitter/users/batch_by_ids", params={"user_ids": ids_param})
        data = [User.model_validate(item) for item in response.get("data", []) or []]
        return PaginatedResponse(data=data, next_cursor=response.get("next_cursor"))

    async def get_by_usernames(self, usernames: list[str]) -> PaginatedResponse[User]:
        """Get multiple users by their usernames.

        Args:
            usernames: List of usernames (without @) to fetch.

        Returns:
            Paginated response containing the users.

        Example:
            ```python
            users = await client.twitter.users.get_by_usernames(["elonmusk", "sama"])
            for user in users.data:
                print(f"{user.name} (@{user.username})")
            ```
        """
        names_param = ",".join(usernames)
        response = await self._client.get("/v1/twitter/users/batch_by_usernames", params={"usernames": names_param})
        data = [User.model_validate(item) for item in response.get("data", []) or []]
        return PaginatedResponse(data=data, next_cursor=response.get("next_cursor"))

    async def get_mentions(
        self,
        username: str,
        *,
        count: int = 20,
        cursor: str | None = None,
    ) -> PaginatedResponse[Tweet]:
        """Get tweets mentioning a user.

        Args:
            username: The user's username (without @).
            count: Number of tweets per page (default 20).
            cursor: Pagination cursor for fetching more results.

        Returns:
            Paginated response containing mention tweets.

        Example:
            ```python
            mentions = await client.twitter.users.get_mentions("elonmusk")
            for tweet in mentions.data:
                print(f"@{tweet.username}: {tweet.text[:100]}...")
            ```
        """
        response = await self._client.get(
            f"/v1/twitter/users/{username}/mentions",
            params={"count": count, "cursor": cursor},
        )
        data = [Tweet.model_validate(item) for item in response.get("data", []) or []]
        return PaginatedResponse(data=data, next_cursor=response.get("next_cursor"))

    async def get_mentions_all(
        self,
        username: str,
        *,
        count: int = 20,
        max_pages: int | None = None,
        max_items: int | None = None,
    ) -> AsyncIterator[Tweet]:
        """Iterate through all mentions with automatic pagination.

        Args:
            username: The user's username (without @).
            count: Number of tweets per page (default 20).
            max_pages: Maximum number of pages to fetch.
            max_items: Maximum number of tweets to yield.

        Yields:
            Tweet objects mentioning the user.
        """
        async for tweet in paginate(
            self._client,
            f"/v1/twitter/users/{username}/mentions",
            {"count": count},
            Tweet.model_validate,
            max_pages=max_pages,
            max_items=max_items,
        ):
            yield tweet

    async def get_articles(
        self,
        user_id: str,
        *,
        count: int = 20,
        cursor: str | None = None,
    ) -> PaginatedResponse[Tweet]:
        """Get long-form articles by a user.

        Args:
            user_id: The user's numeric ID.
            count: Number of articles per page (default 20).
            cursor: Pagination cursor for fetching more results.

        Returns:
            Paginated response containing article tweets.

        Example:
            ```python
            articles = await client.twitter.users.get_articles("44196397")
            for article in articles.data:
                print(f"{article.created_at}: {article.text[:100]}...")
            ```
        """
        response = await self._client.get(
            f"/v1/twitter/users/{user_id}/articles",
            params={"count": count, "cursor": cursor},
        )
        data = [Tweet.model_validate(item) for item in response.get("data", []) or []]
        return PaginatedResponse(data=data, next_cursor=response.get("next_cursor"))

    async def get_articles_all(
        self,
        user_id: str,
        *,
        count: int = 20,
        max_pages: int | None = None,
        max_items: int | None = None,
    ) -> AsyncIterator[Tweet]:
        """Iterate through all articles with automatic pagination.

        Args:
            user_id: The user's numeric ID.
            count: Number of articles per page (default 20).
            max_pages: Maximum number of pages to fetch.
            max_items: Maximum number of tweets to yield.

        Yields:
            Tweet objects representing articles by the user.
        """
        async for tweet in paginate(
            self._client,
            f"/v1/twitter/users/{user_id}/articles",
            {"count": count},
            Tweet.model_validate,
            max_pages=max_pages,
            max_items=max_items,
        ):
            yield tweet
