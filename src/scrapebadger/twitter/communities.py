"""Twitter Communities API client.

Provides methods for fetching Twitter communities, members, and tweets.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from scrapebadger._internal.pagination import PaginatedResponse, paginate
from scrapebadger.twitter.models import Community, CommunityMember, CommunityTweetType, Tweet

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from scrapebadger._internal.client import BaseClient


class CommunitiesClient:
    """Client for Twitter communities endpoints.

    Provides async methods for fetching community details, members,
    moderators, and tweets.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            # Search communities
            communities = await client.twitter.communities.search("python")

            # Get community details
            community = await client.twitter.communities.get_detail("123456")
            print(f"{community.name}: {community.member_count} members")

            # Get community tweets
            tweets = await client.twitter.communities.get_tweets("123456")
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize communities client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def get_detail(self, community_id: str) -> Community:
        """Get details for a specific community.

        Args:
            community_id: The community ID.

        Returns:
            The community details including rules and admin info.

        Raises:
            NotFoundError: If the community doesn't exist.

        Example:
            ```python
            community = await client.twitter.communities.get_detail("123456")
            print(f"{community.name}")
            print(f"Members: {community.member_count:,}")
            print(f"Join policy: {community.join_policy}")

            if community.rules:
                print("Rules:")
                for rule in community.rules:
                    print(f"  - {rule.name}")
            ```
        """
        response = await self._client.get(f"/v1/twitter/communities/{community_id}")
        return Community.model_validate(response)

    async def get_tweets(
        self,
        community_id: str,
        *,
        tweet_type: CommunityTweetType = CommunityTweetType.TOP,
        count: int = 40,
        cursor: str | None = None,
    ) -> PaginatedResponse[Tweet]:
        """Get tweets from a community.

        Args:
            community_id: The community ID.
            tweet_type: Type of tweets (TOP, LATEST, or MEDIA).
            count: Number of tweets per page (1-100).
            cursor: Pagination cursor for fetching more results.

        Returns:
            Paginated response containing community tweets.

        Example:
            ```python
            # Get top tweets
            tweets = await client.twitter.communities.get_tweets("123456")

            # Get latest tweets
            tweets = await client.twitter.communities.get_tweets(
                "123456",
                tweet_type=CommunityTweetType.LATEST
            )
            ```
        """
        response = await self._client.get(
            f"/v1/twitter/communities/{community_id}/tweets",
            params={
                "tweet_type": tweet_type.value,
                "count": count,
                "cursor": cursor,
            },
        )
        data = [Tweet.model_validate(item) for item in response.get("data", []) or []]
        return PaginatedResponse(data=data, next_cursor=response.get("next_cursor"))

    async def get_tweets_all(
        self,
        community_id: str,
        *,
        tweet_type: CommunityTweetType = CommunityTweetType.TOP,
        max_pages: int | None = None,
        max_items: int | None = None,
    ) -> AsyncIterator[Tweet]:
        """Iterate through all community tweets with automatic pagination.

        Args:
            community_id: The community ID.
            tweet_type: Type of tweets (TOP, LATEST, or MEDIA).
            max_pages: Maximum number of pages to fetch.
            max_items: Maximum number of tweets to yield.

        Yields:
            Tweet objects from the community.
        """
        async for tweet in paginate(
            self._client,
            f"/v1/twitter/communities/{community_id}/tweets",
            {"tweet_type": tweet_type.value},
            Tweet.model_validate,
            max_pages=max_pages,
            max_items=max_items,
        ):
            yield tweet

    async def get_members(
        self,
        community_id: str,
        *,
        count: int = 20,
        cursor: str | None = None,
    ) -> PaginatedResponse[CommunityMember]:
        """Get members of a community.

        Args:
            community_id: The community ID.
            count: Number of members per page (1-100).
            cursor: Pagination cursor for fetching more results.

        Returns:
            Paginated response containing community members.

        Example:
            ```python
            members = await client.twitter.communities.get_members("123456")
            for member in members.data:
                print(f"@{member.user.username} ({member.role})")
            ```
        """
        response = await self._client.get(
            f"/v1/twitter/communities/{community_id}/members",
            params={"count": count, "cursor": cursor},
        )
        # Community members have a nested structure
        raw_data = response.get("data", []) or []
        data = []
        for item in raw_data:
            # If the API returns User directly, wrap it
            if "user" not in item:
                from scrapebadger.twitter.models import User

                data.append(
                    CommunityMember(
                        user=User.model_validate(item),
                        role=item.get("role"),
                        joined_at=item.get("joined_at"),
                    )
                )
            else:
                data.append(CommunityMember.model_validate(item))

        return PaginatedResponse(data=data, next_cursor=response.get("next_cursor"))

    async def get_moderators(
        self,
        community_id: str,
        *,
        count: int = 20,
        cursor: str | None = None,
    ) -> PaginatedResponse[CommunityMember]:
        """Get moderators of a community.

        Args:
            community_id: The community ID.
            count: Number of moderators per page (1-100).
            cursor: Pagination cursor for fetching more results.

        Returns:
            Paginated response containing community moderators.
        """
        response = await self._client.get(
            f"/v1/twitter/communities/{community_id}/moderators",
            params={"count": count, "cursor": cursor},
        )
        raw_data = response.get("data", []) or []
        data = []
        for item in raw_data:
            if "user" not in item:
                from scrapebadger.twitter.models import User

                data.append(
                    CommunityMember(
                        user=User.model_validate(item),
                        role="moderator",
                        joined_at=item.get("joined_at"),
                    )
                )
            else:
                data.append(CommunityMember.model_validate(item))

        return PaginatedResponse(data=data, next_cursor=response.get("next_cursor"))

    async def search(
        self,
        query: str,
        *,
        cursor: str | None = None,
    ) -> PaginatedResponse[Community]:
        """Search for communities.

        Args:
            query: Search query string.
            cursor: Pagination cursor for fetching more results.

        Returns:
            Paginated response containing matching communities.

        Example:
            ```python
            results = await client.twitter.communities.search("python developers")
            for community in results.data:
                print(f"{community.name}: {community.member_count} members")
            ```
        """
        response = await self._client.get(
            "/v1/twitter/communities/search",
            params={"query": query, "cursor": cursor},
        )
        data = [Community.model_validate(item) for item in response.get("data", []) or []]
        return PaginatedResponse(data=data, next_cursor=response.get("next_cursor"))

    async def search_tweets(
        self,
        community_id: str,
        query: str,
        *,
        count: int = 20,
        cursor: str | None = None,
    ) -> PaginatedResponse[Tweet]:
        """Search for tweets within a community.

        Args:
            community_id: The community ID.
            query: Search query string.
            count: Number of tweets per page (1-100).
            cursor: Pagination cursor for fetching more results.

        Returns:
            Paginated response containing matching tweets.
        """
        response = await self._client.get(
            f"/v1/twitter/communities/{community_id}/search_tweets",
            params={"query": query, "count": count, "cursor": cursor},
        )
        data = [Tweet.model_validate(item) for item in response.get("data", []) or []]
        return PaginatedResponse(data=data, next_cursor=response.get("next_cursor"))

    async def get_timeline(
        self,
        *,
        count: int = 20,
        cursor: str | None = None,
    ) -> PaginatedResponse[Tweet]:
        """Get the community timeline (tweets from communities you're in).

        Args:
            count: Number of tweets per page (1-100).
            cursor: Pagination cursor for fetching more results.

        Returns:
            Paginated response containing community timeline tweets.
        """
        response = await self._client.get(
            "/v1/twitter/communities/timeline",
            params={"count": count, "cursor": cursor},
        )
        data = [Tweet.model_validate(item) for item in response.get("data", []) or []]
        return PaginatedResponse(data=data, next_cursor=response.get("next_cursor"))
