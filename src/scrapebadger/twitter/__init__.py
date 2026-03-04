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
from scrapebadger.twitter.stream import StreamClient, verify_webhook_signature
from scrapebadger.twitter.stream_models import (
    BillingLog,
    BillingLogList,
    ConnectedEvent,
    DeliveryLog,
    DeliveryLogList,
    ErrorEvent,
    FilterRuleDeliveryLog,
    FilterRuleDeliveryLogList,
    FilterRulePricingTier,
    FilterRulePricingTierList,
    FilterRuleQueryValidation,
    FilterRuleResponse,
    FilterRuleResponseList,
    FilterRuleStatus,
    MonitorStatus,
    PingEvent,
    StreamEvent,
    StreamEventType,
    StreamMonitor,
    StreamMonitorList,
    StreamTweet,
    TweetEvent,
)

__all__ = [
    "BillingLog",
    "BillingLogList",
    "Community",
    "CommunityBanner",
    "CommunityMember",
    "CommunityRule",
    # Stream WebSocket event models
    "ConnectedEvent",
    "DeliveryLog",
    "DeliveryLogList",
    "ErrorEvent",
    # Filter rule models
    "FilterRuleDeliveryLog",
    "FilterRuleDeliveryLogList",
    "FilterRulePricingTier",
    "FilterRulePricingTierList",
    "FilterRuleQueryValidation",
    "FilterRuleResponse",
    "FilterRuleResponseList",
    # Filter rule enums
    "FilterRuleStatus",
    "Hashtag",
    "List",
    "Location",
    # Nested models
    "Media",
    # Stream enums
    "MonitorStatus",
    "PingEvent",
    "Place",
    "PlaceTrends",
    "Poll",
    "PollOption",
    # Enums
    "QueryType",
    # Stream client
    "StreamClient",
    "StreamEvent",
    "StreamEventType",
    # Stream models
    "StreamMonitor",
    "StreamMonitorList",
    "StreamTweet",
    "Trend",
    "TrendCategory",
    # Core models
    "Tweet",
    "TweetEvent",
    # Client
    "TwitterClient",
    "Url",
    "User",
    "UserAbout",
    "UserIds",
    "UserMention",
    # Webhook verification
    "verify_webhook_signature",
]
