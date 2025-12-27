"""Twitter Lists API client.

Provides methods for fetching Twitter lists, list members, and list tweets.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from scrapebadger._internal.pagination import PaginatedResponse, paginate
from scrapebadger.twitter.models import List, Tweet, User

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from scrapebadger._internal.client import BaseClient


class ListsClient:
    """Client for Twitter lists endpoints.

    Provides async methods for fetching list details, members, subscribers,
    and tweets from lists.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            # Search for lists
            lists = await client.twitter.lists.search("tech leaders")

            # Get list details
            lst = await client.twitter.lists.get_detail("123456")
            print(f"{lst.name}: {lst.member_count} members")

            # Get list tweets
            tweets = await client.twitter.lists.get_tweets("123456")
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize lists client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def get_detail(self, list_id: str) -> List:
        """Get details for a specific list.

        Args:
            list_id: The list ID.

        Returns:
            The list details.

        Raises:
            NotFoundError: If the list doesn't exist.

        Example:
            ```python
            lst = await client.twitter.lists.get_detail("123456")
            print(f"{lst.name} by @{lst.username}")
            print(f"{lst.member_count} members, {lst.subscriber_count} subscribers")
            ```
        """
        response = await self._client.get(f"/v1/twitter/lists/{list_id}/detail")
        return List.model_validate(response)

    async def get_tweets(
        self,
        list_id: str,
        *,
        cursor: str | None = None,
    ) -> PaginatedResponse[Tweet]:
        """Get tweets from a list's timeline.

        Args:
            list_id: The list ID.
            cursor: Pagination cursor for fetching more results.

        Returns:
            Paginated response containing tweets from list members.

        Example:
            ```python
            tweets = await client.twitter.lists.get_tweets("123456")
            for tweet in tweets.data:
                print(f"@{tweet.username}: {tweet.text[:100]}...")
            ```
        """
        response = await self._client.get(
            f"/v1/twitter/lists/{list_id}/tweets",
            params={"cursor": cursor},
        )
        data = [Tweet.model_validate(item) for item in response.get("data", []) or []]
        return PaginatedResponse(data=data, next_cursor=response.get("next_cursor"))

    async def get_tweets_all(
        self,
        list_id: str,
        *,
        max_pages: int | None = None,
        max_items: int | None = None,
    ) -> AsyncIterator[Tweet]:
        """Iterate through all list tweets with automatic pagination.

        Args:
            list_id: The list ID.
            max_pages: Maximum number of pages to fetch.
            max_items: Maximum number of tweets to yield.

        Yields:
            Tweet objects from the list timeline.
        """
        async for tweet in paginate(
            self._client,
            f"/v1/twitter/lists/{list_id}/tweets",
            {},
            Tweet.model_validate,
            max_pages=max_pages,
            max_items=max_items,
        ):
            yield tweet

    async def get_members(
        self,
        list_id: str,
        *,
        cursor: str | None = None,
    ) -> PaginatedResponse[User]:
        """Get members of a list.

        Args:
            list_id: The list ID.
            cursor: Pagination cursor for fetching more results.

        Returns:
            Paginated response containing list members.

        Example:
            ```python
            members = await client.twitter.lists.get_members("123456")
            for user in members.data:
                print(f"@{user.username}")
            ```
        """
        response = await self._client.get(
            f"/v1/twitter/lists/{list_id}/members",
            params={"cursor": cursor},
        )
        data = [User.model_validate(item) for item in response.get("data", []) or []]
        return PaginatedResponse(data=data, next_cursor=response.get("next_cursor"))

    async def get_members_all(
        self,
        list_id: str,
        *,
        max_pages: int | None = None,
        max_items: int | None = None,
    ) -> AsyncIterator[User]:
        """Iterate through all list members with automatic pagination.

        Args:
            list_id: The list ID.
            max_pages: Maximum number of pages to fetch.
            max_items: Maximum number of users to yield.

        Yields:
            User objects for each list member.
        """
        async for user in paginate(
            self._client,
            f"/v1/twitter/lists/{list_id}/members",
            {},
            User.model_validate,
            max_pages=max_pages,
            max_items=max_items,
        ):
            yield user

    async def get_subscribers(
        self,
        list_id: str,
        *,
        count: int = 20,
        cursor: str | None = None,
    ) -> PaginatedResponse[User]:
        """Get subscribers of a list.

        Args:
            list_id: The list ID.
            count: Number of users per page.
            cursor: Pagination cursor for fetching more results.

        Returns:
            Paginated response containing list subscribers.
        """
        response = await self._client.get(
            f"/v1/twitter/lists/{list_id}/subscribers",
            params={"count": count, "cursor": cursor},
        )
        data = [User.model_validate(item) for item in response.get("data", []) or []]
        return PaginatedResponse(data=data, next_cursor=response.get("next_cursor"))

    async def search(
        self,
        query: str,
        *,
        count: int = 20,
        cursor: str | None = None,
    ) -> PaginatedResponse[List]:
        """Search for lists.

        Args:
            query: Search query string.
            count: Number of lists per page.
            cursor: Pagination cursor for fetching more results.

        Returns:
            Paginated response containing matching lists.

        Example:
            ```python
            results = await client.twitter.lists.search("tech leaders")
            for lst in results.data:
                print(f"{lst.name}: {lst.member_count} members")
            ```
        """
        response = await self._client.get(
            "/v1/twitter/lists/search",
            params={"query": query, "count": count, "cursor": cursor},
        )
        data = [List.model_validate(item) for item in response.get("data", []) or []]
        return PaginatedResponse(data=data, next_cursor=response.get("next_cursor"))

    async def get_my_lists(
        self,
        *,
        count: int = 100,
        cursor: str | None = None,
    ) -> PaginatedResponse[List]:
        """Get lists owned by the authenticated user.

        Args:
            count: Number of lists per page.
            cursor: Pagination cursor for fetching more results.

        Returns:
            Paginated response containing the user's lists.
        """
        response = await self._client.get(
            "/v1/twitter/lists/my_lists",
            params={"count": count, "cursor": cursor},
        )
        data = [List.model_validate(item) for item in response.get("data", []) or []]
        return PaginatedResponse(data=data, next_cursor=response.get("next_cursor"))
