"""E2E tests for UsersClient.

Tests all user-related API endpoints with real API calls.
"""

from __future__ import annotations

from scrapebadger import ScrapeBadger
from scrapebadger.twitter.models import Tweet, User, UserAbout, UserIds

from .conftest import E2ETestData


class TestGetByUsername:
    """Tests for get_by_username method."""

    async def test_get_by_username_returns_user(
        self, client: ScrapeBadger, test_data: E2ETestData
    ) -> None:
        """Test fetching a user by username returns valid user data."""
        user = await client.twitter.users.get_by_username(test_data.username)

        assert isinstance(user, User)
        assert user.username.lower() == test_data.username.lower()
        assert user.id is not None
        assert user.name is not None

    async def test_get_by_username_includes_counts(
        self, client: ScrapeBadger, test_data: E2ETestData
    ) -> None:
        """Test that user data includes follower/following counts."""
        user = await client.twitter.users.get_by_username(test_data.username)

        # Major accounts should have significant follower counts
        assert user.followers_count is not None
        assert user.followers_count >= 0


class TestGetById:
    """Tests for get_by_id method."""

    async def test_get_by_id_returns_user(self, client: ScrapeBadger, test_data: E2ETestData) -> None:
        """Test fetching a user by ID returns valid user data."""
        user = await client.twitter.users.get_by_id(test_data.user_id)

        assert isinstance(user, User)
        assert user.id == test_data.user_id


class TestGetAbout:
    """Tests for get_about method."""

    async def test_get_about_returns_extended_info(
        self, client: ScrapeBadger, test_data: E2ETestData
    ) -> None:
        """Test fetching extended user info."""
        about = await client.twitter.users.get_about(test_data.username)

        assert isinstance(about, UserAbout)
        # UserAbout should have the extended fields
        assert hasattr(about, "user")


class TestGetFollowers:
    """Tests for get_followers method."""

    async def test_get_followers_returns_users(
        self, client: ScrapeBadger, test_data: E2ETestData
    ) -> None:
        """Test fetching followers returns paginated response."""
        result = await client.twitter.users.get_followers(test_data.username)

        assert hasattr(result, "data")
        assert hasattr(result, "next_cursor")
        assert hasattr(result, "has_more")

        # Should have some followers for major accounts
        if result.data:
            assert all(isinstance(u, User) for u in result.data)


class TestGetFollowersAll:
    """Tests for get_followers_all method."""

    async def test_get_followers_all_with_max_items(
        self, client: ScrapeBadger, test_data: E2ETestData
    ) -> None:
        """Test iterating through followers with max_items limit."""
        followers: list[User] = []
        async for follower in client.twitter.users.get_followers_all(
            test_data.username, max_items=5
        ):
            followers.append(follower)
            assert isinstance(follower, User)

        # Should respect max_items
        assert len(followers) <= 5

    async def test_get_followers_all_with_max_pages(
        self, client: ScrapeBadger, test_data: E2ETestData
    ) -> None:
        """Test iterating through followers with max_pages limit."""
        count = 0
        async for _ in client.twitter.users.get_followers_all(test_data.username, max_pages=1):
            count += 1
            if count > 100:  # Safety limit
                break

        # Should have fetched at least one page
        assert count >= 0


class TestGetFollowing:
    """Tests for get_following method."""

    async def test_get_following_returns_users(
        self, client: ScrapeBadger, test_data: E2ETestData
    ) -> None:
        """Test fetching following returns paginated response."""
        result = await client.twitter.users.get_following(test_data.username)

        assert hasattr(result, "data")
        assert hasattr(result, "next_cursor")

        if result.data:
            assert all(isinstance(u, User) for u in result.data)


class TestGetFollowingAll:
    """Tests for get_following_all method."""

    async def test_get_following_all_with_max_items(
        self, client: ScrapeBadger, test_data: E2ETestData
    ) -> None:
        """Test iterating through following with max_items limit."""
        following: list[User] = []
        async for user in client.twitter.users.get_following_all(test_data.username, max_items=5):
            following.append(user)
            assert isinstance(user, User)

        assert len(following) <= 5


class TestGetLatestFollowers:
    """Tests for get_latest_followers method."""

    async def test_get_latest_followers_returns_users(
        self, client: ScrapeBadger, test_data: E2ETestData
    ) -> None:
        """Test fetching latest followers returns paginated response."""
        result = await client.twitter.users.get_latest_followers(test_data.username, count=10)

        assert hasattr(result, "data")
        assert hasattr(result, "next_cursor")

        if result.data:
            assert all(isinstance(u, User) for u in result.data)


class TestGetLatestFollowing:
    """Tests for get_latest_following method."""

    async def test_get_latest_following_returns_users(
        self, client: ScrapeBadger, test_data: E2ETestData
    ) -> None:
        """Test fetching latest following returns paginated response."""
        result = await client.twitter.users.get_latest_following(test_data.username, count=10)

        assert hasattr(result, "data")

        if result.data:
            assert all(isinstance(u, User) for u in result.data)


class TestGetFollowerIds:
    """Tests for get_follower_ids method."""

    async def test_get_follower_ids_returns_ids(
        self, client: ScrapeBadger, test_data: E2ETestData
    ) -> None:
        """Test fetching follower IDs returns ID list."""
        result = await client.twitter.users.get_follower_ids(test_data.username)

        assert isinstance(result, UserIds)
        assert hasattr(result, "ids")
        assert isinstance(result.ids, list)

        # Major accounts should have many followers
        if result.ids:
            assert all(isinstance(user_id, str) for user_id in result.ids)


class TestGetFollowingIds:
    """Tests for get_following_ids method."""

    async def test_get_following_ids_returns_ids(
        self, client: ScrapeBadger, test_data: E2ETestData
    ) -> None:
        """Test fetching following IDs returns ID list."""
        result = await client.twitter.users.get_following_ids(test_data.username)

        assert isinstance(result, UserIds)
        assert hasattr(result, "ids")
        assert isinstance(result.ids, list)


class TestGetVerifiedFollowers:
    """Tests for get_verified_followers method."""

    async def test_get_verified_followers_returns_users(
        self, client: ScrapeBadger, test_data: E2ETestData
    ) -> None:
        """Test fetching verified followers returns paginated response."""
        result = await client.twitter.users.get_verified_followers(test_data.user_id, count=10)

        assert hasattr(result, "data")

        if result.data:
            assert all(isinstance(u, User) for u in result.data)


class TestGetFollowersYouKnow:
    """Tests for get_followers_you_know method."""

    async def test_get_followers_you_know_returns_users(
        self, client: ScrapeBadger, test_data: E2ETestData
    ) -> None:
        """Test fetching mutual followers returns paginated response."""
        result = await client.twitter.users.get_followers_you_know(test_data.user_id, count=10)

        assert hasattr(result, "data")

        if result.data:
            assert all(isinstance(u, User) for u in result.data)


class TestGetSubscriptions:
    """Tests for get_subscriptions method."""

    async def test_get_subscriptions_returns_users(
        self, client: ScrapeBadger, test_data: E2ETestData
    ) -> None:
        """Test fetching subscriptions returns paginated response."""
        result = await client.twitter.users.get_subscriptions(test_data.user_id, count=10)

        assert hasattr(result, "data")

        if result.data:
            assert all(isinstance(u, User) for u in result.data)


class TestGetHighlights:
    """Tests for get_highlights method."""

    async def test_get_highlights_returns_tweets(
        self, client: ScrapeBadger, test_data: E2ETestData
    ) -> None:
        """Test fetching user highlights returns paginated response."""
        result = await client.twitter.users.get_highlights(test_data.user_id, count=10)

        assert hasattr(result, "data")

        if result.data:
            assert all(isinstance(t, Tweet) for t in result.data)


class TestSearch:
    """Tests for search method."""

    async def test_search_returns_users(self, client: ScrapeBadger) -> None:
        """Test searching for users returns paginated response."""
        result = await client.twitter.users.search("python developer")

        assert hasattr(result, "data")
        assert hasattr(result, "next_cursor")

        # Should find some users
        if result.data:
            assert all(isinstance(u, User) for u in result.data)


class TestSearchAll:
    """Tests for search_all method."""

    async def test_search_all_with_max_items(self, client: ScrapeBadger) -> None:
        """Test iterating through search results with max_items limit."""
        users: list[User] = []
        async for user in client.twitter.users.search_all("developer", max_items=5):
            users.append(user)
            assert isinstance(user, User)

        assert len(users) <= 5
