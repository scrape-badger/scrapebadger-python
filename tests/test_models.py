"""Tests for Pydantic models."""

from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError

from scrapebadger.twitter.models import (
    Community,
    CommunityRule,
    CommunityTweetType,
    Hashtag,
    List,
    Location,
    Media,
    Place,
    PlaceTrends,
    Poll,
    PollOption,
    QueryType,
    Trend,
    TrendCategory,
    Tweet,
    TweetPlace,
    Url,
    User,
    UserAbout,
    UserIds,
    UserMention,
)


class TestEnums:
    """Tests for enum types."""

    def test_query_type_values(self) -> None:
        """Test QueryType enum values."""
        assert QueryType.TOP == "Top"
        assert QueryType.LATEST == "Latest"
        assert QueryType.MEDIA == "Media"

    def test_trend_category_values(self) -> None:
        """Test TrendCategory enum values."""
        assert TrendCategory.TRENDING == "trending"
        assert TrendCategory.FOR_YOU == "for_you"
        assert TrendCategory.NEWS == "news"
        assert TrendCategory.SPORTS == "sports"
        assert TrendCategory.ENTERTAINMENT == "entertainment"

    def test_community_tweet_type_values(self) -> None:
        """Test CommunityTweetType enum values."""
        assert CommunityTweetType.TOP == "Top"
        assert CommunityTweetType.LATEST == "Latest"
        assert CommunityTweetType.MEDIA == "Media"


class TestTweetModel:
    """Tests for Tweet model."""

    def test_minimal_tweet(self) -> None:
        """Test tweet with minimal data."""
        tweet = Tweet(id="123")
        assert tweet.id == "123"
        assert tweet.text == ""
        assert tweet.favorite_count == 0

    def test_full_tweet(self, sample_tweet_data: dict[str, Any]) -> None:
        """Test tweet with full data."""
        tweet = Tweet.model_validate(sample_tweet_data)
        assert tweet.id == "1234567890123456789"
        assert "Python" in tweet.text
        assert tweet.username == "elonmusk"
        assert tweet.favorite_count == 50000

    def test_tweet_is_frozen(self, sample_tweet_data: dict[str, Any]) -> None:
        """Test tweet is immutable."""
        tweet = Tweet.model_validate(sample_tweet_data)
        with pytest.raises(ValidationError):
            tweet.text = "Modified"  # type: ignore[misc]

    def test_tweet_with_media(self) -> None:
        """Test tweet with media attachments."""
        data = {
            "id": "123",
            "text": "Check this out!",
            "media": [
                {"type": "photo", "url": "https://example.com/image.jpg"},
                {"type": "video", "url": "https://example.com/video.mp4"},
            ],
        }
        tweet = Tweet.model_validate(data)
        assert len(tweet.media) == 2
        assert tweet.media[0].type == "photo"
        assert tweet.media[1].type == "video"

    def test_tweet_with_poll(self) -> None:
        """Test tweet with poll."""
        data = {
            "id": "123",
            "text": "Vote!",
            "poll": {
                "id": "poll123",
                "voting_status": "open",
                "options": [
                    {"position": 1, "label": "Option A", "votes": 100},
                    {"position": 2, "label": "Option B", "votes": 200},
                ],
            },
        }
        tweet = Tweet.model_validate(data)
        assert tweet.poll is not None
        assert tweet.poll.id == "poll123"
        assert len(tweet.poll.options) == 2

    def test_created_at_datetime_property(self) -> None:
        """Test created_at_datetime property."""
        tweet = Tweet(id="123", created_at="2024-01-15T12:00:00Z")
        dt = tweet.created_at_datetime
        assert dt is not None
        assert dt.year == 2024
        assert dt.month == 1
        assert dt.day == 15


class TestUserModel:
    """Tests for User model."""

    def test_minimal_user(self) -> None:
        """Test user with minimal data."""
        user = User(id="123", username="test")
        assert user.id == "123"
        assert user.username == "test"
        assert user.followers_count == 0

    def test_full_user(self, sample_user_data: dict[str, Any]) -> None:
        """Test user with full data."""
        user = User.model_validate(sample_user_data)
        assert user.id == "44196397"
        assert user.username == "elonmusk"
        assert user.name == "Elon Musk"
        assert user.followers_count == 150000000

    def test_user_is_frozen(self, sample_user_data: dict[str, Any]) -> None:
        """Test user is immutable."""
        user = User.model_validate(sample_user_data)
        with pytest.raises(ValidationError):
            user.username = "newname"  # type: ignore[misc]


class TestUserAboutModel:
    """Tests for UserAbout model."""

    def test_user_about(self) -> None:
        """Test UserAbout model."""
        data = {
            "id": "123",
            "screen_name": "test",
            "account_based_in": "United States",
            "username_changes": 2,
            "is_identity_verified": True,
        }
        about = UserAbout.model_validate(data)
        assert about.id == "123"
        assert about.account_based_in == "United States"
        assert about.username_changes == 2
        assert about.is_identity_verified is True


class TestUserIdsModel:
    """Tests for UserIds model."""

    def test_user_ids(self) -> None:
        """Test UserIds model."""
        ids = UserIds(ids=[1, 2, 3, 4, 5], next_cursor="abc123")
        assert len(ids.ids) == 5
        assert ids.next_cursor == "abc123"


class TestListModel:
    """Tests for List model."""

    def test_list_model(self, sample_list_data: dict[str, Any]) -> None:
        """Test List model."""
        lst = List.model_validate(sample_list_data)
        assert lst.id == "1234567890"
        assert lst.name == "Tech Leaders"
        assert lst.member_count == 50


class TestCommunityModel:
    """Tests for Community model."""

    def test_community_model(self, sample_community_data: dict[str, Any]) -> None:
        """Test Community model."""
        community = Community.model_validate(sample_community_data)
        assert community.id == "1234567890"
        assert community.name == "Python Developers"
        assert community.member_count == 50000
        assert community.rules is not None
        assert len(community.rules) == 2


class TestTrendModel:
    """Tests for Trend model."""

    def test_trend_model(self, sample_trend_data: dict[str, Any]) -> None:
        """Test Trend model."""
        trend = Trend.model_validate(sample_trend_data)
        assert trend.name == "#Python"
        assert trend.tweet_count == 50000


class TestPlaceModel:
    """Tests for Place model."""

    def test_place_model(self, sample_place_data: dict[str, Any]) -> None:
        """Test Place model."""
        place = Place.model_validate(sample_place_data)
        assert place.id == "5a110d312052166f"
        assert place.name == "San Francisco"
        assert place.country == "United States"


class TestLocationModel:
    """Tests for Location model."""

    def test_location_model(self) -> None:
        """Test Location model."""
        loc = Location(
            woeid=23424977,
            name="United States",
            country="United States",
            country_code="US",
            place_type="Country",
        )
        assert loc.woeid == 23424977
        assert loc.country_code == "US"


class TestPlaceTrendsModel:
    """Tests for PlaceTrends model."""

    def test_place_trends_model(self) -> None:
        """Test PlaceTrends model."""
        place_trends = PlaceTrends(
            woeid=23424977,
            name="United States",
            trends=[
                Trend(name="#Python", tweet_count=50000),
                Trend(name="#JavaScript", tweet_count=30000),
            ],
        )
        assert place_trends.woeid == 23424977
        assert len(place_trends.trends) == 2


class TestNestedModels:
    """Tests for nested models."""

    def test_media_model(self) -> None:
        """Test Media model."""
        media = Media(type="photo", url="https://example.com/image.jpg")
        assert media.type == "photo"
        assert media.url == "https://example.com/image.jpg"

    def test_poll_option_model(self) -> None:
        """Test PollOption model."""
        option = PollOption(position=1, label="Option A", votes=100)
        assert option.position == 1
        assert option.label == "Option A"
        assert option.votes == 100

    def test_poll_model(self) -> None:
        """Test Poll model."""
        poll = Poll(
            id="123",
            voting_status="open",
            options=[
                PollOption(position=1, label="A", votes=10),
                PollOption(position=2, label="B", votes=20),
            ],
        )
        assert poll.id == "123"
        assert len(poll.options) == 2

    def test_url_model(self) -> None:
        """Test Url model."""
        url = Url(
            url="https://t.co/abc",
            expanded_url="https://example.com/page",
            display_url="example.com/page",
        )
        assert url.expanded_url == "https://example.com/page"

    def test_hashtag_model(self) -> None:
        """Test Hashtag model."""
        hashtag = Hashtag(tag="Python")
        assert hashtag.tag == "Python"

    def test_user_mention_model(self) -> None:
        """Test UserMention model."""
        mention = UserMention(id="123", username="test", name="Test User")
        assert mention.username == "test"

    def test_tweet_place_model(self) -> None:
        """Test TweetPlace model."""
        place = TweetPlace(
            id="123",
            full_name="San Francisco, CA",
            country="United States",
        )
        assert place.full_name == "San Francisco, CA"

    def test_community_rule_model(self) -> None:
        """Test CommunityRule model."""
        rule = CommunityRule(id="1", name="Be nice", description="Be respectful")
        assert rule.name == "Be nice"
