"""E2E tests for ListsClient.

Tests all list-related API endpoints with real API calls.
"""

from __future__ import annotations

import pytest

from scrapebadger import ScrapeBadger
from scrapebadger.twitter.models import List, Tweet, User

from .conftest import E2ETestData


class TestGetDetail:
    """Tests for get_detail method."""

    async def test_get_detail_returns_list(self, client: ScrapeBadger, test_data: E2ETestData) -> None:
        """Test fetching list details returns valid list data."""
        lst = await client.twitter.lists.get_detail(test_data.list_id)

        assert isinstance(lst, List)
        assert lst.id == test_data.list_id
        assert lst.name is not None

    async def test_get_detail_includes_counts(
        self, client: ScrapeBadger, test_data: E2ETestData
    ) -> None:
        """Test that list data includes member/subscriber counts."""
        lst = await client.twitter.lists.get_detail(test_data.list_id)

        assert lst.member_count is not None
        assert lst.member_count >= 0


class TestGetTweets:
    """Tests for get_tweets method."""

    async def test_get_tweets_returns_tweets(
        self, client: ScrapeBadger, test_data: E2ETestData
    ) -> None:
        """Test fetching list tweets returns paginated response."""
        result = await client.twitter.lists.get_tweets(test_data.list_id)

        assert hasattr(result, "data")
        assert hasattr(result, "next_cursor")
        assert hasattr(result, "has_more")

        if result.data:
            assert all(isinstance(t, Tweet) for t in result.data)


class TestGetTweetsAll:
    """Tests for get_tweets_all method."""

    async def test_get_tweets_all_with_max_items(
        self, client: ScrapeBadger, test_data: E2ETestData
    ) -> None:
        """Test iterating through list tweets with max_items limit."""
        tweets: list[Tweet] = []
        async for tweet in client.twitter.lists.get_tweets_all(test_data.list_id, max_items=5):
            tweets.append(tweet)
            assert isinstance(tweet, Tweet)

        assert len(tweets) <= 5


class TestGetMembers:
    """Tests for get_members method."""

    async def test_get_members_returns_users(
        self, client: ScrapeBadger, test_data: E2ETestData
    ) -> None:
        """Test fetching list members returns paginated response."""
        result = await client.twitter.lists.get_members(test_data.list_id)

        assert hasattr(result, "data")
        assert hasattr(result, "next_cursor")

        if result.data:
            assert all(isinstance(u, User) for u in result.data)


class TestGetMembersAll:
    """Tests for get_members_all method."""

    async def test_get_members_all_with_max_items(
        self, client: ScrapeBadger, test_data: E2ETestData
    ) -> None:
        """Test iterating through list members with max_items limit."""
        members: list[User] = []
        async for user in client.twitter.lists.get_members_all(test_data.list_id, max_items=5):
            members.append(user)
            assert isinstance(user, User)

        assert len(members) <= 5


class TestGetSubscribers:
    """Tests for get_subscribers method."""

    async def test_get_subscribers_returns_users(
        self, client: ScrapeBadger, test_data: E2ETestData
    ) -> None:
        """Test fetching list subscribers returns paginated response."""
        result = await client.twitter.lists.get_subscribers(test_data.list_id, count=10)

        assert hasattr(result, "data")
        assert hasattr(result, "next_cursor")

        if result.data:
            assert all(isinstance(u, User) for u in result.data)


class TestSearch:
    """Tests for search method."""

    async def test_search_returns_lists(self, client: ScrapeBadger) -> None:
        """Test searching for lists returns paginated response."""
        result = await client.twitter.lists.search("tech", count=10)

        assert hasattr(result, "data")
        assert hasattr(result, "next_cursor")

        if result.data:
            assert all(isinstance(lst, List) for lst in result.data)

    async def test_search_with_different_queries(self, client: ScrapeBadger) -> None:
        """Test search with various query strings."""
        result = await client.twitter.lists.search("technology leaders", count=5)

        assert hasattr(result, "data")


class TestGetMyLists:
    """Tests for get_my_lists method."""

    @pytest.mark.skip(reason="Requires authenticated session with lists")
    async def test_get_my_lists_returns_lists(self, client: ScrapeBadger) -> None:
        """Test fetching user's own lists returns paginated response.

        Note: This test may return empty results if the authenticated
        account doesn't own any lists.
        """
        result = await client.twitter.lists.get_my_lists(count=10)

        assert hasattr(result, "data")
        assert hasattr(result, "next_cursor")

        if result.data:
            assert all(isinstance(lst, List) for lst in result.data)
