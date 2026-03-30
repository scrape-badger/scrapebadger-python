"""Stream monitoring models for Twitter Streams API.

This module contains all Pydantic models for the Twitter Streams feature,
including monitor management, WebSocket event types, and log models.
All models are immutable (frozen) for safe concurrent use.
"""

from __future__ import annotations

import sys
from datetime import datetime  # noqa: TC003 (Pydantic needs this at runtime)
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from enum import Enum

    class StrEnum(str, Enum):
        """String enum for Python 3.10 compatibility."""


# =============================================================================
# Base Configuration
# =============================================================================


class _BaseModel(BaseModel):
    """Base model with common configuration.

    All stream models are frozen (immutable) to prevent accidental mutation
    and to support safe use in concurrent async contexts.
    """

    model_config = ConfigDict(
        frozen=True,
        populate_by_name=True,
        extra="ignore",
        str_strip_whitespace=True,
    )


# =============================================================================
# Enums
# =============================================================================


class MonitorStatus(StrEnum):
    """Lifecycle status of a stream monitor.

    Attributes:
        ACTIVE: Monitor is running and polling.
        PAUSED: Monitor paused by user or auto-paused by billing.
        ERROR: Monitor paused due to persistent scraper error.
    """

    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"


class StreamEventType(StrEnum):
    """Type discriminator for WebSocket events.

    Attributes:
        CONNECTED: Sent immediately after successful WebSocket upgrade.
        PING: Server keepalive ping (SDK auto-replies with pong).
        TWEET: A new tweet detected by a monitor.
        ERROR: Server-side error (typically before connection close).
    """

    CONNECTED = "connected"
    PING = "ping"
    TWEET = "tweet"
    ERROR = "error"


# =============================================================================
# Monitor Models
# =============================================================================


class StreamMonitor(_BaseModel):
    """A stream monitor watching a set of Twitter accounts.

    Attributes:
        id: UUID of the monitor.
        name: Human-readable label.
        usernames: Lowercased Twitter handles being monitored.
        poll_interval_seconds: How often the monitor polls (float seconds).
        status: Current lifecycle state.
        status_reason: Human-readable reason for non-active status (None if active).
        webhook_url: HTTPS delivery URL, or None.
        webhook_secret_set: Whether a webhook signing secret is configured.
        estimated_credits_per_hour: Projected credit burn rate.
        pricing_tier: Tier label (Ultra, High, Standard, Low, Minimal).
        created_at: ISO timestamp of creation.
        updated_at: ISO timestamp of last modification.

    Example:
        ```python
        monitor = await client.twitter.stream.create_monitor(
            name="Tech Leaders",
            usernames=["elonmusk", "naval"],
            poll_interval_seconds=5.0,
        )
        print(f"{monitor.name}: tier={monitor.pricing_tier}, status={monitor.status}")
        ```
    """

    id: str
    name: str
    usernames: list[str] = Field(default_factory=list)
    poll_interval_seconds: float
    status: MonitorStatus
    status_reason: str | None = None
    webhook_url: str | None = None
    webhook_secret_set: bool = False
    estimated_credits_per_hour: float = 0.0
    pricing_tier: str = ""
    created_at: datetime
    updated_at: datetime


class StreamMonitorList(_BaseModel):
    """Paginated list of stream monitors.

    Attributes:
        monitors: The monitors on this page.
        total: Total count across all pages.
        page: Current page number (1-indexed).
        page_size: Number of items per page.

    Example:
        ```python
        result = await client.twitter.stream.list_monitors()
        pages = result.total // result.page_size + 1
        print(f"Total: {result.total}, page {result.page} of {pages}")
        ```
    """

    monitors: list[StreamMonitor] = Field(default_factory=list)
    total: int
    page: int
    page_size: int


# =============================================================================
# WebSocket Event Models
# =============================================================================


class StreamTweet(_BaseModel):
    """A tweet payload embedded inside a StreamEvent.

    This is the same shape as the server-side tweet snapshot stored at
    detection time. It mirrors the Tweet model but is not identical:
    some fields may be absent depending on what the scraper captured.

    Attributes:
        id: Tweet ID (Snowflake string).
        text: Tweet text content.
        created_at: Raw string from Twikit (e.g. 'Mon Mar 03 09:59:57 +0000 2026').
        user_id: Author numeric ID as string.
        username: Author handle (without @).
        user_name: Author display name.
        favorite_count: Like count at detection time.
        retweet_count: Retweet count at detection time.
        reply_count: Reply count at detection time.
        media: Attached media items.
        urls: URL entities.
        hashtags: Hashtag entities.
    """

    id: str
    text: str = ""
    created_at: str | None = None
    user_id: str | None = None
    username: str | None = None
    user_name: str | None = None
    favorite_count: int = 0
    retweet_count: int = 0
    reply_count: int = 0
    media: list[dict[str, Any]] = Field(default_factory=list)
    urls: list[dict[str, Any]] = Field(default_factory=list)
    hashtags: list[dict[str, Any]] = Field(default_factory=list)


class ConnectedEvent(_BaseModel):
    """Emitted immediately after a successful WebSocket upgrade.

    Attributes:
        type: Always "connected".
        connection_id: Server-assigned UUID for this connection.
        api_key_id: The API key identifier used for this connection.
    """

    type: StreamEventType = StreamEventType.CONNECTED
    connection_id: str
    api_key_id: str


class PingEvent(_BaseModel):
    """Keepalive ping from the server. SDK handles pong reply automatically.

    The SDK transparently sends a pong response and then yields this event
    to the caller so the caller can observe server keepalives if needed.

    Attributes:
        type: Always "ping".
        timestamp: Server timestamp in ISO format.
    """

    type: StreamEventType = StreamEventType.PING
    timestamp: str


class TweetEvent(_BaseModel):
    """A new tweet detected by one of the caller's monitors.

    Attributes:
        type: Always "tweet".
        monitor_id: UUID of the monitor that detected this tweet.
        tweet_id: The Snowflake tweet ID as a string.
        author_username: Lowercased Twitter handle of the author.
        tweet_published_at: ISO timestamp decoded from Snowflake.
        detected_at: ISO timestamp of server-side detection.
        latency_ms: Milliseconds between tweet publish and detection.
        tweet: Full tweet data snapshot.

    Example:
        ```python
        async with client.twitter.stream.connect() as events:
            async for event in events:
                if isinstance(event, TweetEvent):
                    print(f"@{event.author_username}: {event.tweet.text}")
                    print(f"  latency: {event.latency_ms}ms")
        ```
    """

    type: StreamEventType = StreamEventType.TWEET
    monitor_id: str
    tweet_id: str
    author_username: str
    tweet_published_at: datetime
    detected_at: datetime
    latency_ms: int
    tweet: StreamTweet


class ErrorEvent(_BaseModel):
    """Server-side error event (sent before connection close on auth failures).

    Attributes:
        type: Always "error".
        code: Numeric error code (4001 = auth, 4003 = connection limit).
        message: Human-readable error description.
    """

    type: StreamEventType = StreamEventType.ERROR
    code: int
    message: str


# Union type: callers can narrow on .type
StreamEvent = ConnectedEvent | PingEvent | TweetEvent | ErrorEvent


# =============================================================================
# Log Models
# =============================================================================


class DeliveryLog(_BaseModel):
    """A tweet delivery log entry.

    Attributes:
        id: UUID.
        monitor_id: UUID of the monitor.
        monitor_name: Monitor display name.
        tweet_id: Snowflake tweet ID.
        author_username: Twitter handle.
        tweet_text_preview: First 100 chars of tweet text.
        tweet_url: Canonical twitter.com URL.
        tweet_published_at: Snowflake-decoded publish time.
        detected_at: Server detection timestamp.
        latency_ms: Milliseconds between publish and detection.
        latency_badge: Visual badge ("green", "yellow", "red").
        delivery_status: "websocket_delivered", "webhook_delivered", "webhook_failed".
        webhook_status_code: HTTP status returned by webhook endpoint, or None.
        webhook_attempts: Number of webhook delivery attempts.
    """

    id: str
    monitor_id: str
    monitor_name: str
    tweet_id: str
    author_username: str
    tweet_text_preview: str | None = None
    tweet_url: str
    tweet_published_at: datetime
    detected_at: datetime
    latency_ms: int
    latency_badge: str
    delivery_status: str
    webhook_status_code: int | None = None
    webhook_attempts: int = 0


class DeliveryLogList(_BaseModel):
    """Paginated tweet delivery logs.

    Attributes:
        logs: The delivery log entries on this page.
        total: Total count across all pages.
        page: Current page number (1-indexed).
        page_size: Number of items per page.
    """

    logs: list[DeliveryLog] = Field(default_factory=list)
    total: int
    page: int
    page_size: int


class BillingLog(_BaseModel):
    """A billing activity log entry.

    Attributes:
        id: UUID.
        monitor_id: UUID of the monitor.
        monitor_name: Monitor display name.
        billed_at: Timestamp of the billing tick.
        num_accounts: Number of accounts billed.
        credits_deducted: Total credits deducted this tick.
        tier_label: Pricing tier at time of billing.
        rate_applied: Credits per account per tick applied.
    """

    id: str
    monitor_id: str
    monitor_name: str
    billed_at: datetime
    num_accounts: int
    credits_deducted: float
    tier_label: str
    rate_applied: float


class BillingLogList(_BaseModel):
    """Paginated billing activity logs.

    Attributes:
        logs: The billing log entries on this page.
        total: Total count across all pages.
        page: Current page number (1-indexed).
        page_size: Number of items per page.
    """

    logs: list[BillingLog] = Field(default_factory=list)
    total: int
    page: int
    page_size: int


# =============================================================================
# Filter Rule Models
# =============================================================================


class FilterRuleStatus(StrEnum):
    """Lifecycle status of a filter rule.

    Attributes:
        ACTIVE: Rule is running and polling.
        PAUSED: Rule paused by user or auto-paused by billing.
        ERROR: Rule paused due to persistent scraper error.
        INACTIVE: Rule inactive pending activation.
    """

    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"
    INACTIVE = "inactive"


class FilterRuleResponse(_BaseModel):
    """A filter rule monitoring a search query for matching tweets.

    Filter rules use Twitter search syntax to watch for tweets matching a
    query, polling on a configurable interval.

    Attributes:
        id: UUID of the filter rule.
        tag: Human-readable label for the rule.
        query: Twitter advanced search query string.
        interval_seconds: Polling interval in seconds.
        status: Current lifecycle state.
        status_reason: Human-readable reason for non-active status (None if active).
        webhook_url: HTTPS delivery URL, or None.
        webhook_secret_set: Whether a webhook signing secret is configured.
        max_results_per_poll: Maximum tweets to return per polling cycle.
        credits_per_rule_per_day: Credit burn rate per day for this rule.
        pricing_tier: Tier label derived from interval_seconds.
        created_at: ISO timestamp of creation.
        updated_at: ISO timestamp of last modification.

    Example:
        ```python
        rule = await client.twitter.stream.create_filter_rule(
            tag="Python news",
            query="#python lang:en -is:retweet",
            interval_seconds=60.0,
        )
        print(f"{rule.tag}: tier={rule.pricing_tier}, status={rule.status}")
        ```
    """

    id: str
    tag: str
    query: str
    interval_seconds: float
    status: FilterRuleStatus
    status_reason: str | None = None
    webhook_url: str | None = None
    webhook_secret_set: bool = False
    max_results_per_poll: int = 10
    credits_per_rule_per_day: float = 0.0
    pricing_tier: str = ""
    created_at: str
    updated_at: str


class FilterRuleResponseList(_BaseModel):
    """Paginated list of filter rules.

    Attributes:
        rules: The filter rules on this page.
        total: Total count across all pages.
        limit: Maximum items per page.
        offset: Number of items skipped.

    Example:
        ```python
        result = await client.twitter.stream.list_filter_rules()
        print(f"Total: {result.total}")
        for rule in result.rules:
            print(f"  {rule.tag}: {rule.status}")
        ```
    """

    rules: list[FilterRuleResponse] = Field(default_factory=list)
    total: int
    limit: int
    offset: int


class FilterRuleDeliveryLog(_BaseModel):
    """A tweet delivery log entry for a filter rule.

    Attributes:
        id: UUID of the log entry.
        rule_id: UUID of the filter rule.
        rule_tag: Tag of the filter rule.
        tweet_id: Snowflake tweet ID.
        author_username: Twitter handle of the tweet author.
        tweet_text_preview: First characters of tweet text.
        tweet_url: Canonical twitter.com URL.
        tweet_published_at: Snowflake-decoded publish time (ISO string).
        detected_at: Server detection timestamp (ISO string).
        latency_ms: Milliseconds between tweet publish and detection.
        latency_badge: Visual badge ("green", "yellow", "red").
        delivery_status: Delivery outcome string.
        webhook_status_code: HTTP status from webhook endpoint, or None.
        webhook_attempts: Number of webhook delivery attempts.
    """

    id: str
    rule_id: str
    rule_tag: str
    tweet_id: str
    author_username: str
    tweet_text_preview: str | None = None
    tweet_url: str
    tweet_published_at: str
    detected_at: str
    latency_ms: int
    latency_badge: str
    delivery_status: str
    webhook_status_code: int | None = None
    webhook_attempts: int = 0


class FilterRuleDeliveryLogList(_BaseModel):
    """Paginated tweet delivery logs for filter rules.

    Attributes:
        logs: The delivery log entries on this page.
        total: Total count across all pages.
        limit: Maximum items per page.
        offset: Number of items skipped.
    """

    logs: list[FilterRuleDeliveryLog] = Field(default_factory=list)
    total: int
    limit: int
    offset: int


class FilterRulePricingTier(_BaseModel):
    """A pricing tier for filter rules.

    Attributes:
        id: UUID of the pricing tier.
        tier_label: Human-readable tier name (e.g. "Standard").
        max_interval_seconds: Maximum interval in seconds for this tier.
        credits_per_rule_per_day: Cost in credits per rule per day.
        display_order: Ordering for display purposes (lower = faster/pricier).

    Example:
        ```python
        pricing = await client.twitter.stream.get_filter_rule_pricing()
        for tier in pricing.tiers:
            print(f"{tier.tier_label}: {tier.credits_per_rule_per_day} cr/day")
        ```
    """

    id: str
    tier_label: str
    max_interval_seconds: float
    credits_per_rule_per_day: float
    display_order: int


class FilterRulePricingTierList(_BaseModel):
    """List of available filter rule pricing tiers.

    Attributes:
        tiers: All configured pricing tiers, ordered by display_order.
    """

    tiers: list[FilterRulePricingTier] = Field(default_factory=list)


class FilterRuleQueryValidation(_BaseModel):
    """Result of a filter rule query validation check.

    Attributes:
        valid: Whether the query syntax is valid.
        error: Human-readable error message if invalid, None if valid.
        sample_results: Number of matching tweets found in a sample check.

    Example:
        ```python
        result = await client.twitter.stream.validate_filter_rule_query(
            "#python lang:en -is:retweet"
        )
        if result.valid:
            print(f"Valid query, found {result.sample_results} sample results")
        else:
            print(f"Invalid query: {result.error}")
        ```
    """

    valid: bool
    error: str | None = None
    sample_results: int = 0
