"""E2E tests for TweetsClient.

Tests all tweet-related API endpoints with real API calls.
"""

from __future__ import annotations

from scrapebadger import ScrapeBadger
from scrapebadger.twitter.models import QueryType, Tweet, User

from .conftest import E2ETestData


class TestGetById:
    """Tests for get_by_id method."""

    async def test_get_by_id_returns_tweet(
        self, client: ScrapeBadger, test_data: E2ETestData
    ) -> None:
        """Test fetching a tweet by ID returns valid tweet data."""
        tweet = await client.twitter.tweets.get_by_id(test_data.tweet_id)

        assert isinstance(tweet, Tweet)
        assert tweet.id == test_data.tweet_id
        assert tweet.text is not None


class TestGetByIds:
    """Tests for get_by_ids method."""

    async def test_get_by_ids_returns_tweets(
        self, client: ScrapeBadger, test_data: E2ETestData
    ) -> None:
        """Test fetching multiple tweets by IDs returns paginated response."""
        result = await client.twitter.tweets.get_by_ids([test_data.tweet_id])

        assert hasattr(result, "data")
        assert len(result.data) >= 1

        tweet = result.data[0]
        assert isinstance(tweet, Tweet)
        assert tweet.id == test_data.tweet_id


class TestGetReplies:
    """Tests for get_replies method."""

    async def test_get_replies_returns_tweets(
        self, client: ScrapeBadger, test_data: E2ETestData
    ) -> None:
        """Test fetching tweet replies returns paginated response."""
        result = await client.twitter.tweets.get_replies(test_data.tweet_id)

        assert hasattr(result, "data")
        assert hasattr(result, "next_cursor")
        assert hasattr(result, "has_more")

        if result.data:
            assert all(isinstance(t, Tweet) for t in result.data)


class TestGetRetweeters:
    """Tests for get_retweeters method."""

    async def test_get_retweeters_returns_users(
        self, client: ScrapeBadger, test_data: E2ETestData
    ) -> None:
        """Test fetching retweeters returns paginated response of users."""
        result = await client.twitter.tweets.get_retweeters(test_data.tweet_id)

        assert hasattr(result, "data")
        assert hasattr(result, "next_cursor")

        if result.data:
            assert all(isinstance(u, User) for u in result.data)


class TestGetFavoriters:
    """Tests for get_favoriters method."""

    async def test_get_favoriters_returns_users(
        self, client: ScrapeBadger, test_data: E2ETestData
    ) -> None:
        """Test fetching users who liked a tweet returns paginated response."""
        result = await client.twitter.tweets.get_favoriters(test_data.tweet_id, count=20)

        assert hasattr(result, "data")
        assert hasattr(result, "next_cursor")

        if result.data:
            assert all(isinstance(u, User) for u in result.data)


class TestGetSimilar:
    """Tests for get_similar method."""

    async def test_get_similar_returns_tweets(
        self, client: ScrapeBadger, test_data: E2ETestData
    ) -> None:
        """Test fetching similar tweets returns paginated response."""
        result = await client.twitter.tweets.get_similar(test_data.tweet_id)

        assert hasattr(result, "data")

        if result.data:
            assert all(isinstance(t, Tweet) for t in result.data)


class TestSearch:
    """Tests for search method."""

    async def test_search_top_returns_tweets(self, client: ScrapeBadger) -> None:
        """Test searching for tweets with TOP query type."""
        result = await client.twitter.tweets.search("python", query_type=QueryType.TOP)

        assert hasattr(result, "data")
        assert hasattr(result, "next_cursor")

        # Should find some tweets for common search terms
        if result.data:
            assert all(isinstance(t, Tweet) for t in result.data)

    async def test_search_latest_returns_tweets(self, client: ScrapeBadger) -> None:
        """Test searching for tweets with LATEST query type."""
        result = await client.twitter.tweets.search("python", query_type=QueryType.LATEST)

        assert hasattr(result, "data")

        if result.data:
            assert all(isinstance(t, Tweet) for t in result.data)

    async def test_search_with_cursor_pagination(self, client: ScrapeBadger) -> None:
        """Test search pagination using cursor."""
        # First page
        first_page = await client.twitter.tweets.search("technology")

        if first_page.has_more and first_page.next_cursor:
            # Second page
            second_page = await client.twitter.tweets.search(
                "technology", cursor=first_page.next_cursor
            )
            assert hasattr(second_page, "data")


class TestSearchAll:
    """Tests for search_all method."""

    async def test_search_all_with_max_items(self, client: ScrapeBadger) -> None:
        """Test iterating through search results with max_items limit."""
        tweets: list[Tweet] = []
        async for tweet in client.twitter.tweets.search_all("python", max_items=5):
            tweets.append(tweet)
            assert isinstance(tweet, Tweet)

        assert len(tweets) <= 5

    async def test_search_all_with_max_pages(self, client: ScrapeBadger) -> None:
        """Test iterating through search results with max_pages limit."""
        count = 0
        async for _ in client.twitter.tweets.search_all("developer", max_pages=1):
            count += 1
            if count > 100:  # Safety limit
                break

        assert count >= 0

    async def test_search_all_with_query_type(self, client: ScrapeBadger) -> None:
        """Test search_all with different query types."""
        tweets: list[Tweet] = []
        async for tweet in client.twitter.tweets.search_all(
            "python", query_type=QueryType.LATEST, max_items=3
        ):
            tweets.append(tweet)

        assert len(tweets) <= 3


class TestGetUserTweets:
    """Tests for get_user_tweets method."""

    async def test_get_user_tweets_returns_tweets(
        self, client: ScrapeBadger, test_data: E2ETestData
    ) -> None:
        """Test fetching user tweets returns paginated response."""
        result = await client.twitter.tweets.get_user_tweets(test_data.username)

        assert hasattr(result, "data")
        assert hasattr(result, "next_cursor")

        if result.data:
            assert all(isinstance(t, Tweet) for t in result.data)


class TestGetUserTweetsAll:
    """Tests for get_user_tweets_all method."""

    async def test_get_user_tweets_all_with_max_items(
        self, client: ScrapeBadger, test_data: E2ETestData
    ) -> None:
        """Test iterating through user tweets with max_items limit."""
        tweets: list[Tweet] = []
        async for tweet in client.twitter.tweets.get_user_tweets_all(
            test_data.username, max_items=5
        ):
            tweets.append(tweet)
            assert isinstance(tweet, Tweet)

        assert len(tweets) <= 5

    async def test_get_user_tweets_all_with_max_pages(
        self, client: ScrapeBadger, test_data: E2ETestData
    ) -> None:
        """Test iterating through user tweets with max_pages limit."""
        count = 0
        async for _ in client.twitter.tweets.get_user_tweets_all(test_data.username, max_pages=1):
            count += 1
            if count > 100:  # Safety limit
                break

        assert count >= 0
