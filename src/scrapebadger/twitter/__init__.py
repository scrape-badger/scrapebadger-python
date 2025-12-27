"""Twitter API module for ScrapeBadger SDK.

This module provides a comprehensive async client for scraping Twitter data
through the ScrapeBadger API. All methods are async and return strongly-typed
Pydantic models.

Example:
    ```python
    from scrapebadger import ScrapeBadger

    async with ScrapeBadger(api_key="your-key") as client:
        # Get user profile
        user = await client.twitter.users.get_by_username("elonmusk")
        print(f"{user.name} has {user.followers_count:,} followers")

        # Get user's tweets
        tweets = await client.twitter.tweets.get_user_tweets("elonmusk")
        for tweet in tweets.data:
            print(f"- {tweet.text[:100]}...")

        # Search tweets
        async for tweet in client.twitter.tweets.search_all("python programming"):
            print(tweet.text)
    ```
"""

from scrapebadger.twitter.client import TwitterClient
from scrapebadger.twitter.models import (
    Community,
    CommunityBanner,
    CommunityMember,
    CommunityRule,
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
    Url,
    User,
    UserAbout,
    UserIds,
    UserMention,
)

__all__ = [
    "Community",
    "CommunityBanner",
    "CommunityMember",
    "CommunityRule",
    "Hashtag",
    "List",
    "Location",
    # Nested models
    "Media",
    "Place",
    "PlaceTrends",
    "Poll",
    "PollOption",
    # Enums
    "QueryType",
    "Trend",
    "TrendCategory",
    # Core models
    "Tweet",
    # Client
    "TwitterClient",
    "Url",
    "User",
    "UserAbout",
    "UserIds",
    "UserMention",
]
