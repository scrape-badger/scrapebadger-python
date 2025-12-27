"""Pydantic models for Twitter API responses.

This module contains all the data models used by the Twitter API client.
All models are immutable (frozen) and use strict validation for type safety.

Models are organized into:
- Core models: Tweet, User, List, Community, Trend, Place
- Nested models: Media, Poll, Url, Hashtag, etc.
- Enums: QueryType, TrendCategory, CommunityTweetType
"""

from __future__ import annotations

import sys
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from enum import Enum

    class StrEnum(str, Enum):
        """String enum for Python 3.10 compatibility."""

# =============================================================================
# Enums
# =============================================================================


class QueryType(StrEnum):
    """Search query type for tweet searches.

    Attributes:
        TOP: Top/relevant tweets (default).
        LATEST: Most recent tweets.
        MEDIA: Tweets containing media.
    """

    TOP = "Top"
    LATEST = "Latest"
    MEDIA = "Media"


class TrendCategory(StrEnum):
    """Category for trending topics.

    Attributes:
        TRENDING: General trending topics.
        FOR_YOU: Personalized trends.
        NEWS: News-related trends.
        SPORTS: Sports trends.
        ENTERTAINMENT: Entertainment trends.
    """

    TRENDING = "trending"
    FOR_YOU = "for_you"
    NEWS = "news"
    SPORTS = "sports"
    ENTERTAINMENT = "entertainment"


class CommunityTweetType(StrEnum):
    """Tweet type filter for community tweets.

    Attributes:
        TOP: Top/popular tweets.
        LATEST: Most recent tweets.
        MEDIA: Tweets containing media.
    """

    TOP = "Top"
    LATEST = "Latest"
    MEDIA = "Media"


# =============================================================================
# Base Configuration
# =============================================================================


class _BaseModel(BaseModel):
    """Base model with common configuration."""

    model_config = ConfigDict(
        frozen=True,
        populate_by_name=True,
        extra="ignore",
        str_strip_whitespace=True,
    )


# =============================================================================
# Nested Models
# =============================================================================


class Media(_BaseModel):
    """Media attachment on a tweet.

    Represents images, videos, or animated GIFs attached to tweets.

    Attributes:
        media_key: Unique identifier for the media.
        type: Media type ('photo', 'video', 'animated_gif').
        url: Direct URL to the media.
        preview_image_url: URL to a preview/thumbnail image.
        width: Media width in pixels.
        height: Media height in pixels.
        duration_ms: Duration in milliseconds (for videos).
        view_count: Number of views (for videos).
        alt_text: Accessibility description.
    """

    media_key: str | None = None
    type: str | None = None
    url: str | None = None
    preview_image_url: str | None = None
    width: int | None = None
    height: int | None = None
    duration_ms: int | None = None
    view_count: int | None = None
    alt_text: str | None = None


class PollOption(_BaseModel):
    """A single option in a poll.

    Attributes:
        position: Option position (1-indexed).
        label: Option text.
        votes: Number of votes received.
    """

    position: int
    label: str
    votes: int = 0


class Poll(_BaseModel):
    """A poll attached to a tweet.

    Attributes:
        id: Unique poll identifier.
        voting_status: Current status ('open' or 'closed').
        end_datetime: When the poll ends/ended.
        duration_minutes: Total poll duration.
        options: List of poll options with vote counts.
    """

    id: str | None = None
    voting_status: str | None = None
    end_datetime: str | None = None
    duration_minutes: int | None = None
    options: list[PollOption] = Field(default_factory=list)


class Url(_BaseModel):
    """A URL entity in tweet text.

    Attributes:
        url: The t.co shortened URL.
        expanded_url: The fully expanded URL.
        display_url: The display version of the URL.
        title: Page title (if available).
        description: Page description (if available).
    """

    url: str | None = None
    expanded_url: str | None = None
    display_url: str | None = None
    title: str | None = None
    description: str | None = None


class Hashtag(_BaseModel):
    """A hashtag entity in tweet text.

    Attributes:
        tag: The hashtag text (without #).
    """

    tag: str


class UserMention(_BaseModel):
    """A user mention entity in tweet text.

    Attributes:
        id: User ID of mentioned user.
        username: Username of mentioned user (without @).
        name: Display name of mentioned user.
    """

    id: str | None = None
    username: str | None = None
    name: str | None = None


class TweetPlace(_BaseModel):
    """Location information attached to a tweet.

    Attributes:
        id: Place ID.
        full_name: Full place name.
        name: Short place name.
        country: Country name.
        country_code: ISO country code.
        place_type: Type of place ('city', 'country', etc.).
    """

    id: str | None = None
    full_name: str | None = None
    name: str | None = None
    country: str | None = None
    country_code: str | None = None
    place_type: str | None = None


# =============================================================================
# Core Models
# =============================================================================


class Tweet(_BaseModel):
    """A Twitter tweet with all associated data.

    This is the primary model for tweet data, containing the tweet content,
    engagement metrics, author information, and all entities.

    Attributes:
        id: Unique tweet identifier.
        text: Tweet text content.
        full_text: Full tweet text (may differ from text for long tweets).
        created_at: Tweet creation timestamp (ISO format).
        lang: Language code.

        user_id: Author's user ID.
        username: Author's username.
        user_name: Author's display name.

        favorite_count: Number of likes.
        retweet_count: Number of retweets.
        reply_count: Number of replies.
        quote_count: Number of quote tweets.
        view_count: Number of views.
        bookmark_count: Number of bookmarks.

        favorited: Whether the authenticated user liked this.
        retweeted: Whether the authenticated user retweeted this.
        bookmarked: Whether the authenticated user bookmarked this.

        possibly_sensitive: Whether the tweet is marked as sensitive.
        is_quote_status: Whether this is a quote tweet.
        is_retweet: Whether this is a retweet.

        conversation_id: ID of the conversation thread.
        in_reply_to_status_id: ID of the tweet being replied to.
        in_reply_to_user_id: ID of the user being replied to.

        media: List of attached media.
        urls: List of URLs in the tweet.
        hashtags: List of hashtags.
        user_mentions: List of user mentions.
        poll: Poll data if present.
        place: Location data if present.

        quoted_status_id: ID of the quoted tweet.
        retweeted_status_id: ID of the original retweeted tweet.

        edit_tweet_ids: IDs of edit history.
        editable_until_msecs: Edit deadline timestamp.
        edits_remaining: Remaining edit count.
        is_edit_eligible: Whether the tweet can be edited.

        has_card: Whether the tweet has a link preview card.
        thumbnail_url: Card thumbnail URL.
        thumbnail_title: Card title.

        has_community_notes: Whether the tweet has community notes.
        source: Client used to post the tweet.

    Example:
        ```python
        tweet = await client.twitter.tweets.get_by_id("1234567890")
        print(f"@{tweet.username}: {tweet.text}")
        print(f"Likes: {tweet.favorite_count:,}, Retweets: {tweet.retweet_count:,}")
        ```
    """

    # Core identifiers
    id: str
    text: str = ""
    full_text: str | None = None
    created_at: str | None = None
    lang: str | None = None

    # Author info
    user_id: str | None = None
    username: str | None = None
    user_name: str | None = None

    # Engagement metrics
    favorite_count: int = 0
    retweet_count: int = 0
    reply_count: int = 0
    quote_count: int = 0
    view_count: int | None = None
    bookmark_count: int | None = None

    # User interaction states
    favorited: bool = False
    retweeted: bool = False
    bookmarked: bool = False

    # Tweet properties
    possibly_sensitive: bool = False
    is_quote_status: bool = False
    is_retweet: bool = False
    conversation_id: str | None = None
    in_reply_to_status_id: str | None = None
    in_reply_to_user_id: str | None = None

    # Rich content
    media: list[Media] = Field(default_factory=list)
    urls: list[Url] = Field(default_factory=list)
    hashtags: list[Hashtag] = Field(default_factory=list)
    user_mentions: list[UserMention] = Field(default_factory=list)
    poll: Poll | None = None
    place: TweetPlace | None = None

    # Referenced tweets
    quoted_status_id: str | None = None
    retweeted_status_id: str | None = None

    # Edit information
    edit_tweet_ids: list[str] | None = None
    editable_until_msecs: int | None = None
    edits_remaining: int | None = None
    is_edit_eligible: bool | None = None

    # Card/preview
    has_card: bool | None = None
    thumbnail_url: str | None = None
    thumbnail_title: str | None = None

    # Community notes
    has_community_notes: bool | None = None

    # Source
    source: str | None = None

    @property
    def created_at_datetime(self) -> datetime | None:
        """Parse created_at to datetime object."""
        if self.created_at:
            try:
                return datetime.fromisoformat(self.created_at.replace("Z", "+00:00"))
            except ValueError:
                return None
        return None


class User(_BaseModel):
    """A Twitter user profile.

    Contains all publicly available information about a Twitter user,
    including profile details, metrics, and relationship status.

    Attributes:
        id: Unique user identifier.
        username: User's handle (without @).
        name: Display name.

        description: User's bio.
        location: User-provided location.
        url: User's website URL.
        profile_image_url: Profile picture URL.
        profile_banner_url: Banner image URL.

        followers_count: Number of followers.
        following_count: Number of accounts followed.
        tweet_count: Total tweets posted.
        listed_count: Number of lists the user is on.
        favourites_count: Number of tweets liked.
        media_count: Number of media posts.

        verified: Whether the user is verified (legacy).
        verified_type: Type of verification.
        is_blue_verified: Whether the user has Twitter Blue.

        created_at: Account creation timestamp.
        protected: Whether the account is protected/private.
        possibly_sensitive: Whether content may be sensitive.

        followed_by: Whether they follow the authenticated user.
        following: Whether the authenticated user follows them.
        blocking: Whether the authenticated user blocks them.
        muting: Whether the authenticated user mutes them.
        can_dm: Whether DMs are allowed.

        pinned_tweet_ids: IDs of pinned tweets.

    Example:
        ```python
        user = await client.twitter.users.get_by_username("elonmusk")
        print(f"{user.name} (@{user.username})")
        print(f"Followers: {user.followers_count:,}")
        print(f"Bio: {user.description}")
        ```
    """

    # Core identifiers
    id: str
    username: str
    name: str = ""

    # Profile information
    description: str | None = None
    location: str | None = None
    url: str | None = None
    profile_image_url: str | None = None
    profile_banner_url: str | None = None

    # Account metrics
    followers_count: int = 0
    following_count: int = 0
    tweet_count: int = 0
    listed_count: int = 0
    favourites_count: int | None = None
    media_count: int | None = None

    # Verification and account type
    verified: bool = False
    verified_type: str | None = None
    is_blue_verified: bool | None = None

    # Account dates
    created_at: str | None = None

    # Account settings
    default_profile: bool | None = None
    default_profile_image: bool | None = None
    protected: bool | None = None
    possibly_sensitive: bool | None = None

    # Relationship with authenticated user
    followed_by: bool | None = None
    following: bool | None = None
    follow_request_sent: bool | None = None
    blocking: bool | None = None
    blocked_by: bool | None = None
    muting: bool | None = None
    notifications: bool | None = None
    can_dm: bool | None = None

    # Extended profile features
    has_custom_timelines: bool | None = None
    has_extended_profile: bool | None = None
    is_translator: bool | None = None
    is_translation_enabled: bool | None = None
    professional_type: str | None = None
    advertiser_account_type: str | None = None

    # Engagement
    pinned_tweet_ids: list[str] | None = None
    withheld_in_countries: list[str] | None = None

    @property
    def created_at_datetime(self) -> datetime | None:
        """Parse created_at to datetime object."""
        if self.created_at:
            try:
                return datetime.fromisoformat(self.created_at.replace("Z", "+00:00"))
            except ValueError:
                return None
        return None


class UserAbout(_BaseModel):
    """Extended "About" information for a user.

    Contains additional metadata about a user's account, including
    account location, username change history, and verification details.

    Attributes:
        id: User ID.
        rest_id: REST API user ID.
        screen_name: Username.
        name: Display name.

        account_based_in: Region Twitter believes the account is based in.
        location_accurate: Whether the location is verified.
        affiliate_username: Linked affiliate account.
        source: How the source was determined.

        username_changes: Number of username changes.
        username_last_changed_at: Last change timestamp (ms).
        username_last_changed_at_datetime: Last change as datetime string.

        is_identity_verified: Whether identity is verified.
        verified_since_msec: Verification timestamp (ms).
        verified_since_datetime: Verification as datetime string.

    Example:
        ```python
        about = await client.twitter.users.get_about("elonmusk")
        print(f"Account based in: {about.account_based_in}")
        print(f"Username changes: {about.username_changes}")
        ```
    """

    id: str
    rest_id: str | None = None
    screen_name: str | None = None
    name: str | None = None

    # Location and source information
    account_based_in: str | None = None
    location_accurate: bool | None = None
    affiliate_username: str | None = None
    source: str | None = None

    # Username change history
    username_changes: int | None = None
    username_last_changed_at: int | None = None
    username_last_changed_at_datetime: str | None = None

    # Verification information
    is_identity_verified: bool | None = None
    verified_since_msec: int | None = None
    verified_since_datetime: str | None = None


class UserIds(_BaseModel):
    """Response containing a list of user IDs.

    Used for endpoints that return ID lists without full user data,
    such as follower_ids and following_ids endpoints.

    Attributes:
        ids: List of user IDs.
        next_cursor: Cursor for pagination.

    Example:
        ```python
        ids = await client.twitter.users.get_follower_ids("elonmusk")
        print(f"Found {len(ids.ids):,} follower IDs")
        ```
    """

    ids: list[int] = Field(default_factory=list)
    next_cursor: str | None = None


class List(_BaseModel):
    """A Twitter list.

    Represents a curated list of Twitter users.

    Attributes:
        id: Unique list identifier.
        name: List name.
        description: List description.
        created_at: List creation timestamp.
        member_count: Number of members.
        subscriber_count: Number of subscribers.
        mode: 'public' or 'private'.
        user_id: Owner's user ID.
        username: Owner's username.

    Example:
        ```python
        lists = await client.twitter.lists.search("tech leaders")
        for lst in lists.data:
            print(f"{lst.name}: {lst.member_count} members")
        ```
    """

    id: str
    name: str = ""
    description: str | None = None
    created_at: str | None = None
    member_count: int | None = None
    subscriber_count: int | None = None
    mode: str | None = None
    user_id: str | None = None
    username: str | None = None


class CommunityBanner(_BaseModel):
    """Banner image for a community.

    Attributes:
        url: Banner image URL.
        width: Image width.
        height: Image height.
    """

    url: str | None = None
    width: int | None = None
    height: int | None = None


class CommunityRule(_BaseModel):
    """A rule for a community.

    Attributes:
        id: Rule identifier.
        name: Rule name/title.
        description: Rule description.
    """

    id: str | None = None
    name: str | None = None
    description: str | None = None


class Community(_BaseModel):
    """A Twitter community.

    Represents a community with its members, rules, and settings.

    Attributes:
        id: Unique community identifier.
        name: Community name.
        description: Community description.

        member_count: Number of members.
        is_member: Whether the authenticated user is a member.
        role: User's role ('member', 'moderator', 'admin', 'non_member').

        is_nsfw: Whether the community contains adult content.
        join_policy: How users can join ('Open', 'Closed').
        invites_policy: Who can invite members.
        is_pinned: Whether the community is pinned.

        created_at: Creation timestamp (Unix).
        created_at_datetime: Creation timestamp (ISO).

        banner: Community banner image.
        members_facepile_results: Profile images of some members.

        creator_id: Creator's user ID.
        creator_username: Creator's username.
        creator_name: Creator's display name.
        admin_id: Primary admin's user ID.
        admin_username: Primary admin's username.
        admin_name: Primary admin's display name.

        rules: List of community rules.

    Example:
        ```python
        community = await client.twitter.communities.get_detail("123456")
        print(f"{community.name}: {community.member_count:,} members")
        for rule in community.rules or []:
            print(f"  - {rule.name}")
        ```
    """

    id: str
    name: str = ""
    description: str | None = None

    # Membership information
    member_count: int | None = None
    is_member: bool | None = None
    role: str | None = None

    # Community settings
    is_nsfw: bool | None = None
    join_policy: str | None = None
    invites_policy: str | None = None
    is_pinned: bool | None = None

    # Metadata
    created_at: int | None = None
    created_at_datetime: str | None = None

    # Rich content
    banner: CommunityBanner | None = None
    members_facepile_results: list[str] | None = None

    # Administration
    creator_id: str | None = None
    creator_username: str | None = None
    creator_name: str | None = None
    admin_id: str | None = None
    admin_username: str | None = None
    admin_name: str | None = None

    # Rules
    rules: list[CommunityRule] | None = None


class CommunityMember(_BaseModel):
    """A member of a community.

    Extends User with community-specific information.

    Attributes:
        user: The user data.
        role: Member's role in the community.
        joined_at: When they joined.
    """

    user: User
    role: str | None = None
    joined_at: str | None = None


class Trend(_BaseModel):
    """A trending topic.

    Attributes:
        name: Trend name/hashtag.
        url: Twitter search URL for the trend.
        query: Search query to find tweets.
        tweet_count: Number of tweets (if available).
        domain_context: Category context.

    Example:
        ```python
        trends = await client.twitter.trends.get_trends()
        for trend in trends.data:
            print(f"{trend.name}: {trend.tweet_count or 'N/A'} tweets")
        ```
    """

    name: str
    url: str | None = None
    query: str | None = None
    tweet_count: int | None = None
    domain_context: str | None = None


class Location(_BaseModel):
    """A location for trends.

    Attributes:
        woeid: Where On Earth ID.
        name: Location name.
        country: Country name.
        country_code: ISO country code.
        place_type: Type of place.

    Example:
        ```python
        locations = await client.twitter.trends.get_available_locations()
        us_locations = [loc for loc in locations.data if loc.country_code == "US"]
        ```
    """

    woeid: int
    name: str
    country: str | None = None
    country_code: str | None = None
    place_type: str | None = None


class PlaceTrends(_BaseModel):
    """Trends for a specific location.

    Attributes:
        woeid: Where On Earth ID.
        name: Location name.
        country: Country name.
        trends: List of trends for this location.

    Example:
        ```python
        place_trends = await client.twitter.trends.get_place_trends(23424977)  # US
        print(f"Trends in {place_trends.name}:")
        for trend in place_trends.trends:
            print(f"  - {trend.name}")
        ```
    """

    woeid: int
    name: str | None = None
    country: str | None = None
    trends: list[Trend] = Field(default_factory=list)


class Place(_BaseModel):
    """A geographic place.

    Attributes:
        id: Place ID.
        name: Short place name.
        full_name: Full place name.
        country: Country name.
        country_code: ISO country code.
        place_type: Type of place ('city', 'country', etc.).
        url: Twitter place URL.
        bounding_box: Geographic bounding box.
        attributes: Additional place attributes.

    Example:
        ```python
        places = await client.twitter.geo.search(query="San Francisco")
        for place in places.data:
            print(f"{place.full_name} ({place.place_type})")
        ```
    """

    id: str
    name: str = ""
    full_name: str | None = None
    country: str | None = None
    country_code: str | None = None
    place_type: str | None = None
    url: str | None = None
    bounding_box: dict[str, Any] | None = None
    attributes: dict[str, str] | None = None
