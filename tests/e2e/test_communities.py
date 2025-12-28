"""E2E tests for CommunitiesClient.

Tests all community-related API endpoints with real API calls.
"""

from __future__ import annotations

import pytest

from scrapebadger import ScrapeBadger
from scrapebadger.twitter.models import Community, CommunityMember, CommunityTweetType, Tweet

from .conftest import E2ETestData


class TestGetDetail:
    """Tests for get_detail method."""

    async def test_get_detail_returns_community(
        self, client: ScrapeBadger, test_data: E2ETestData
    ) -> None:
        """Test fetching community details returns valid community data."""
        community = await client.twitter.communities.get_detail(test_data.community_id)

        assert isinstance(community, Community)
        assert community.id == test_data.community_id
        assert community.name is not None

    async def test_get_detail_includes_member_count(
        self, client: ScrapeBadger, test_data: E2ETestData
    ) -> None:
        """Test that community data includes member count."""
        community = await client.twitter.communities.get_detail(test_data.community_id)

        assert community.member_count is not None
        assert community.member_count >= 0


class TestGetTweets:
    """Tests for get_tweets method."""

    async def test_get_tweets_top_returns_tweets(
        self, client: ScrapeBadger, test_data: E2ETestData
    ) -> None:
        """Test fetching top community tweets returns paginated response."""
        result = await client.twitter.communities.get_tweets(
            test_data.community_id, tweet_type=CommunityTweetType.TOP, count=10
        )

        assert hasattr(result, "data")
        assert hasattr(result, "next_cursor")

        if result.data:
            assert all(isinstance(t, Tweet) for t in result.data)

    async def test_get_tweets_latest_returns_tweets(
        self, client: ScrapeBadger, test_data: E2ETestData
    ) -> None:
        """Test fetching latest community tweets returns paginated response."""
        result = await client.twitter.communities.get_tweets(
            test_data.community_id, tweet_type=CommunityTweetType.LATEST, count=10
        )

        assert hasattr(result, "data")

        if result.data:
            assert all(isinstance(t, Tweet) for t in result.data)


class TestGetTweetsAll:
    """Tests for get_tweets_all method."""

    async def test_get_tweets_all_with_max_items(
        self, client: ScrapeBadger, test_data: E2ETestData
    ) -> None:
        """Test iterating through community tweets with max_items limit."""
        tweets: list[Tweet] = []
        async for tweet in client.twitter.communities.get_tweets_all(
            test_data.community_id, max_items=5
        ):
            tweets.append(tweet)
            assert isinstance(tweet, Tweet)

        assert len(tweets) <= 5

    async def test_get_tweets_all_with_tweet_type(
        self, client: ScrapeBadger, test_data: E2ETestData
    ) -> None:
        """Test get_tweets_all with different tweet types."""
        tweets: list[Tweet] = []
        async for tweet in client.twitter.communities.get_tweets_all(
            test_data.community_id,
            tweet_type=CommunityTweetType.LATEST,
            max_items=3,
        ):
            tweets.append(tweet)

        assert len(tweets) <= 3


class TestGetMembers:
    """Tests for get_members method."""

    async def test_get_members_returns_community_members(
        self, client: ScrapeBadger, test_data: E2ETestData
    ) -> None:
        """Test fetching community members returns paginated response."""
        result = await client.twitter.communities.get_members(test_data.community_id, count=10)

        assert hasattr(result, "data")
        assert hasattr(result, "next_cursor")

        if result.data:
            assert all(isinstance(m, CommunityMember) for m in result.data)


class TestGetModerators:
    """Tests for get_moderators method."""

    async def test_get_moderators_returns_community_members(
        self, client: ScrapeBadger, test_data: E2ETestData
    ) -> None:
        """Test fetching community moderators returns paginated response."""
        result = await client.twitter.communities.get_moderators(test_data.community_id, count=10)

        assert hasattr(result, "data")
        assert hasattr(result, "next_cursor")

        if result.data:
            assert all(isinstance(m, CommunityMember) for m in result.data)


class TestSearch:
    """Tests for search method."""

    async def test_search_returns_communities(self, client: ScrapeBadger) -> None:
        """Test searching for communities returns paginated response."""
        result = await client.twitter.communities.search("python")

        assert hasattr(result, "data")
        assert hasattr(result, "next_cursor")

        if result.data:
            assert all(isinstance(c, Community) for c in result.data)

    async def test_search_with_different_queries(self, client: ScrapeBadger) -> None:
        """Test search with various query strings."""
        result = await client.twitter.communities.search("technology")

        assert hasattr(result, "data")


class TestSearchTweets:
    """Tests for search_tweets method."""

    async def test_search_tweets_returns_tweets(
        self, client: ScrapeBadger, test_data: E2ETestData
    ) -> None:
        """Test searching for tweets within a community returns paginated response."""
        result = await client.twitter.communities.search_tweets(
            test_data.community_id, query="hello", count=10
        )

        assert hasattr(result, "data")
        assert hasattr(result, "next_cursor")

        if result.data:
            assert all(isinstance(t, Tweet) for t in result.data)


class TestGetTimeline:
    """Tests for get_timeline method."""

    @pytest.mark.skip(reason="Requires authenticated session with community memberships")
    async def test_get_timeline_returns_tweets(self, client: ScrapeBadger) -> None:
        """Test fetching community timeline returns paginated response.

        Note: This test may return empty results if the authenticated
        account is not a member of any communities.
        """
        result = await client.twitter.communities.get_timeline(count=10)

        assert hasattr(result, "data")
        assert hasattr(result, "next_cursor")

        if result.data:
            assert all(isinstance(t, Tweet) for t in result.data)
