"""Twitter Tweets API client.

Provides methods for fetching tweets, searching, and getting tweet metadata.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from scrapebadger._internal.pagination import PaginatedResponse, paginate
from scrapebadger.twitter.models import QueryType, Tweet, User

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from scrapebadger._internal.client import BaseClient


class TweetsClient:
    """Client for Twitter tweets endpoints.

    Provides async methods for fetching individual tweets, searching tweets,
    and getting tweet engagement data (retweeters, favoriters, replies).

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            # Get single tweet
            tweet = await client.twitter.tweets.get_by_id("1234567890")

            # Search tweets
            results = await client.twitter.tweets.search("python programming")
            for tweet in results.data:
                print(tweet.text)

            # Iterate through all results
            async for tweet in client.twitter.tweets.search_all("python"):
                print(tweet.text)
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize tweets client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def get_by_id(self, tweet_id: str) -> Tweet:
        """Get a single tweet by ID.

        Args:
            tweet_id: The tweet ID to fetch.

        Returns:
            The tweet data.

        Raises:
            NotFoundError: If the tweet doesn't exist.
            AuthenticationError: If the API key is invalid.

        Example:
            ```python
            tweet = await client.twitter.tweets.get_by_id("1234567890")
            print(f"@{tweet.username}: {tweet.text}")
            ```
        """
        response = await self._client.get(f"/v1/twitter/tweets/tweet/{tweet_id}")
        return Tweet.model_validate(response)

    async def get_by_ids(self, tweet_ids: list[str]) -> PaginatedResponse[Tweet]:
        """Get multiple tweets by their IDs.

        Args:
            tweet_ids: List of tweet IDs to fetch.

        Returns:
            Paginated response containing the tweets.

        Example:
            ```python
            tweets = await client.twitter.tweets.get_by_ids([
                "1234567890",
                "0987654321"
            ])
            for tweet in tweets.data:
                print(tweet.text)
            ```
        """
        tweets_param = ",".join(tweet_ids)
        response = await self._client.get(
            "/v1/twitter/tweets/",
            params={"tweets": tweets_param},
        )
        data = [Tweet.model_validate(item) for item in response.get("data", []) or []]
        return PaginatedResponse(data=data, next_cursor=response.get("next_cursor"))

    async def get_replies(
        self,
        tweet_id: str,
        *,
        cursor: str | None = None,
    ) -> PaginatedResponse[Tweet]:
        """Get replies to a tweet.

        Args:
            tweet_id: The tweet ID to get replies for.
            cursor: Pagination cursor for fetching more results.

        Returns:
            Paginated response containing reply tweets.

        Example:
            ```python
            replies = await client.twitter.tweets.get_replies("1234567890")
            for reply in replies.data:
                print(f"@{reply.username}: {reply.text}")

            # Get next page
            if replies.has_more:
                more = await client.twitter.tweets.get_replies(
                    "1234567890",
                    cursor=replies.next_cursor
                )
            ```
        """
        response = await self._client.get(
            f"/v1/twitter/tweets/tweet/{tweet_id}/replies",
            params={"cursor": cursor},
        )
        data = [Tweet.model_validate(item) for item in response.get("data", []) or []]
        return PaginatedResponse(data=data, next_cursor=response.get("next_cursor"))

    async def get_retweeters(
        self,
        tweet_id: str,
        *,
        cursor: str | None = None,
    ) -> PaginatedResponse[User]:
        """Get users who retweeted a tweet.

        Args:
            tweet_id: The tweet ID to get retweeters for.
            cursor: Pagination cursor for fetching more results.

        Returns:
            Paginated response containing users who retweeted.

        Example:
            ```python
            retweeters = await client.twitter.tweets.get_retweeters("1234567890")
            for user in retweeters.data:
                print(f"@{user.username} retweeted")
            ```
        """
        response = await self._client.get(
            f"/v1/twitter/tweets/tweet/{tweet_id}/retweeters",
            params={"cursor": cursor},
        )
        data = [User.model_validate(item) for item in response.get("data", []) or []]
        return PaginatedResponse(data=data, next_cursor=response.get("next_cursor"))

    async def get_favoriters(
        self,
        tweet_id: str,
        *,
        count: int = 40,
        cursor: str | None = None,
    ) -> PaginatedResponse[User]:
        """Get users who liked/favorited a tweet.

        Args:
            tweet_id: The tweet ID to get favoriters for.
            count: Number of users per page (default 40).
            cursor: Pagination cursor for fetching more results.

        Returns:
            Paginated response containing users who liked.

        Example:
            ```python
            likers = await client.twitter.tweets.get_favoriters("1234567890")
            print(f"{len(likers.data)} users liked this tweet")
            ```
        """
        response = await self._client.get(
            f"/v1/twitter/tweets/tweet/{tweet_id}/favoriters",
            params={"count": count, "cursor": cursor},
        )
        data = [User.model_validate(item) for item in response.get("data", []) or []]
        return PaginatedResponse(data=data, next_cursor=response.get("next_cursor"))

    async def get_similar(self, tweet_id: str) -> PaginatedResponse[Tweet]:
        """Get tweets similar to a given tweet.

        Args:
            tweet_id: The tweet ID to find similar tweets for.

        Returns:
            Paginated response containing similar tweets.

        Example:
            ```python
            similar = await client.twitter.tweets.get_similar("1234567890")
            for tweet in similar.data:
                print(f"Similar: {tweet.text[:100]}...")
            ```
        """
        response = await self._client.get(
            f"/v1/twitter/tweets/tweet/{tweet_id}/similar",
        )
        data = [Tweet.model_validate(item) for item in response.get("data", []) or []]
        return PaginatedResponse(data=data, next_cursor=response.get("next_cursor"))

    async def search(
        self,
        query: str,
        *,
        query_type: QueryType = QueryType.TOP,
        cursor: str | None = None,
    ) -> PaginatedResponse[Tweet]:
        """Search for tweets.

        Args:
            query: Search query string. Supports Twitter advanced search operators.
            query_type: Type of search results (TOP, LATEST, or MEDIA).
            cursor: Pagination cursor for fetching more results.

        Returns:
            Paginated response containing matching tweets.

        Example:
            ```python
            # Basic search
            results = await client.twitter.tweets.search("python programming")

            # Latest tweets only
            results = await client.twitter.tweets.search(
                "python",
                query_type=QueryType.LATEST
            )

            # Advanced search operators
            results = await client.twitter.tweets.search(
                "from:elonmusk lang:en"
            )
            ```
        """
        response = await self._client.get(
            "/v1/twitter/tweets/advanced_search",
            params={
                "query": query,
                "query_type": query_type.value,
                "cursor": cursor,
            },
        )
        data = [Tweet.model_validate(item) for item in response.get("data", []) or []]
        return PaginatedResponse(data=data, next_cursor=response.get("next_cursor"))

    async def search_all(
        self,
        query: str,
        *,
        query_type: QueryType = QueryType.TOP,
        max_pages: int | None = None,
        max_items: int | None = None,
    ) -> AsyncIterator[Tweet]:
        """Iterate through all search results with automatic pagination.

        This is a convenience method that automatically handles pagination,
        yielding tweets one at a time.

        Args:
            query: Search query string.
            query_type: Type of search results (TOP, LATEST, or MEDIA).
            max_pages: Maximum number of pages to fetch. None for unlimited.
            max_items: Maximum number of tweets to yield. None for unlimited.

        Yields:
            Tweet objects matching the search query.

        Example:
            ```python
            # Get up to 1000 tweets
            async for tweet in client.twitter.tweets.search_all(
                "python",
                max_items=1000
            ):
                print(tweet.text)

            # Collect into a list
            tweets = [
                t async for t in client.twitter.tweets.search_all(
                    "python",
                    max_pages=5
                )
            ]
            ```
        """
        async for tweet in paginate(
            self._client,
            "/v1/twitter/tweets/advanced_search",
            {"query": query, "query_type": query_type.value},
            Tweet.model_validate,
            max_pages=max_pages,
            max_items=max_items,
        ):
            yield tweet

    async def get_user_tweets(
        self,
        username: str,
        *,
        cursor: str | None = None,
    ) -> PaginatedResponse[Tweet]:
        """Get tweets from a user's timeline.

        Args:
            username: Twitter username (without @).
            cursor: Pagination cursor for fetching more results.

        Returns:
            Paginated response containing the user's tweets.

        Example:
            ```python
            tweets = await client.twitter.tweets.get_user_tweets("elonmusk")
            for tweet in tweets.data:
                print(f"{tweet.created_at}: {tweet.text[:100]}...")
            ```
        """
        response = await self._client.get(
            f"/v1/twitter/users/{username}/latest_tweets",
            params={"cursor": cursor},
        )
        data = [Tweet.model_validate(item) for item in response.get("data", []) or []]
        return PaginatedResponse(data=data, next_cursor=response.get("next_cursor"))

    async def get_user_tweets_all(
        self,
        username: str,
        *,
        max_pages: int | None = None,
        max_items: int | None = None,
    ) -> AsyncIterator[Tweet]:
        """Iterate through all tweets from a user with automatic pagination.

        Args:
            username: Twitter username (without @).
            max_pages: Maximum number of pages to fetch.
            max_items: Maximum number of tweets to yield.

        Yields:
            Tweet objects from the user's timeline.

        Example:
            ```python
            async for tweet in client.twitter.tweets.get_user_tweets_all(
                "elonmusk",
                max_items=500
            ):
                print(tweet.text)
            ```
        """
        async for tweet in paginate(
            self._client,
            f"/v1/twitter/users/{username}/latest_tweets",
            {},
            Tweet.model_validate,
            max_pages=max_pages,
            max_items=max_items,
        ):
            yield tweet
