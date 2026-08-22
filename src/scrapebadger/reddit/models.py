"""Pydantic models for Reddit API responses.

This module contains all the data models used by the Reddit API client.
All models are immutable (frozen) and use strict validation for type safety.

Models are organised into:
- Core models: RedditPost, RedditComment, RedditSubreddit, RedditUser
- Reference models: RedditRule, RedditWikiPage, RedditTrophy, RedditAward
- Nested models: RedditUserSubreddit, RedditModeratedSubreddit
- Response envelopes: SearchPostsResponse, SubredditPostsResponse, etc.

As of 0.10.0, Reddit response models mirror the full set of content/metadata
fields returned by Reddit's authenticated ``.json`` API. Field names, types,
and defaults match the canonical backend scraper model exactly so that API
responses can be passed through ``model_validate`` without any mapping layer.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

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
# Reference / nested models
# =============================================================================


class RedditAward(_BaseModel):
    """An award attached to a post/comment (element of ``all_awardings``)."""

    id: str | None = None
    name: str = ""
    count: int = 0
    coin_price: int = 0
    coin_reward: int = 0
    description: str | None = None
    icon_url: str | None = None
    award_type: str | None = None


class RedditGalleryImage(_BaseModel):
    """One image of a multi-image gallery post, at full source resolution."""

    media_id: str
    url: str
    width: int | None = None
    height: int | None = None
    mime_type: str | None = None
    # Animated ("image/gif") items only: `url` is the .gif, this is the mp4
    # Reddit transcodes for playback. Still images leave it null.
    mp4_url: str | None = None


# =============================================================================
# Core Models
# =============================================================================


class RedditPost(_BaseModel):
    """A Reddit post (submission).

    Field names match the canonical backend model exactly so that API responses
    can be passed through ``model_validate`` without any mapping layer.
    """

    # Identity
    id: str
    fullname: str = ""
    title: str
    author: str = ""
    author_fullname: str | None = None
    # Body
    selftext: str = ""
    selftext_html: str | None = None
    # Link
    url: str = ""
    permalink: str = ""
    domain: str = ""
    # Subreddit
    subreddit: str = ""
    subreddit_id: str | None = None
    subreddit_name_prefixed: str | None = None
    subreddit_type: str | None = None
    subreddit_subscribers: int = 0
    # Score / engagement
    score: int = 0
    ups: int = 0
    downs: int = 0
    upvote_ratio: float = 0.0
    num_comments: int = 0
    num_crossposts: int = 0
    total_awards_received: int = 0
    view_count: int | None = None
    gilded: int = 0
    # Timestamps
    created_utc: float = 0
    created_at: str | None = None
    edited: bool | float = False
    # Content flags / state
    is_self: bool = False
    is_video: bool = False
    is_gallery: bool = False
    is_meta: bool = False
    is_original_content: bool = False
    is_robot_indexable: bool = True
    is_crosspostable: bool = False
    is_reddit_media_domain: bool = False
    media_only: bool = False
    is_nsfw: bool = False
    is_spoiler: bool = False
    is_stickied: bool = False
    locked: bool = False
    archived: bool = False
    pinned: bool = False
    quarantine: bool = False
    hide_score: bool = False
    contest_mode: bool = False
    allow_live_comments: bool = False
    send_replies: bool = False
    distinguished: str | None = None
    removed_by_category: str | None = None
    suggested_sort: str | None = None
    discussion_type: str | None = None
    top_awarded_type: str | None = None
    # Post flair
    link_flair_text: str | None = None
    link_flair_type: str | None = None
    link_flair_css_class: str | None = None
    link_flair_template_id: str | None = None
    link_flair_background_color: str | None = None
    link_flair_text_color: str | None = None
    # Author flair / meta
    author_flair_text: str | None = None
    author_flair_type: str | None = None
    author_flair_css_class: str | None = None
    author_flair_template_id: str | None = None
    author_flair_background_color: str | None = None
    author_flair_text_color: str | None = None
    author_premium: bool = False
    author_patreon_flair: bool = False
    # Media
    thumbnail: str | None = None
    thumbnail_width: int | None = None
    thumbnail_height: int | None = None
    media: dict[str, Any] | None = None
    media_embed: dict[str, Any] | None = None
    secure_media: dict[str, Any] | None = None
    secure_media_embed: dict[str, Any] | None = None
    # Gallery posts (`is_gallery`): the images, in the order the poster set.
    # Empty for every other kind of post.
    gallery_images: list[RedditGalleryImage] = Field(default_factory=list)
    # Awards
    all_awardings: list[RedditAward] = Field(default_factory=list)
    gildings: dict[str, Any] = Field(default_factory=dict)


class RedditComment(_BaseModel):
    """A Reddit comment."""

    id: str
    fullname: str = ""
    body: str = ""
    body_html: str | None = None
    author: str = ""
    author_fullname: str | None = None
    subreddit: str = ""
    subreddit_id: str | None = None
    subreddit_name_prefixed: str | None = None
    subreddit_type: str | None = None
    post_id: str | None = None
    parent_id: str | None = None
    permalink: str = ""
    # Score / engagement
    score: int = 0
    ups: int = 0
    downs: int = 0
    controversiality: int = 0
    total_awards_received: int = 0
    gilded: int = 0
    score_hidden: bool = False
    depth: int = 0
    # Timestamps
    created_utc: float = 0
    created_at: str | None = None
    edited: bool | float = False
    # Flags / state
    is_submitter: bool = False
    is_stickied: bool = False
    locked: bool = False
    archived: bool = False
    collapsed: bool = False
    collapsed_reason: str | None = None
    send_replies: bool = False
    distinguished: str | None = None
    comment_type: str | None = None
    # Author flair / meta
    author_flair_text: str | None = None
    author_flair_type: str | None = None
    author_flair_css_class: str | None = None
    author_flair_template_id: str | None = None
    author_flair_background_color: str | None = None
    author_flair_text_color: str | None = None
    author_premium: bool = False
    # Awards
    all_awardings: list[RedditAward] = Field(default_factory=list)
    gildings: dict[str, Any] = Field(default_factory=dict)
    replies: list[RedditComment] = Field(default_factory=list)


class RedditSubreddit(_BaseModel):
    """A Reddit subreddit (community)."""

    id: str
    fullname: str = ""
    name: str
    display_name_prefixed: str | None = None
    title: str = ""
    description: str = ""
    description_html: str | None = None
    public_description: str = ""
    public_description_html: str | None = None
    url: str = ""
    subscribers: int = 0
    created_utc: float = 0
    created_at: str | None = None
    # Type / flags
    subreddit_type: str | None = None
    lang: str | None = None
    is_nsfw: bool = False
    quarantine: bool = False
    wiki_enabled: bool = False
    over18: bool = False
    # Submission settings
    submission_type: str | None = None
    submit_text: str = ""
    submit_text_html: str | None = None
    submit_text_label: str | None = None
    submit_link_label: str | None = None
    allow_images: bool = False
    allow_videos: bool = False
    allow_galleries: bool = False
    allow_polls: bool = False
    spoilers_enabled: bool = False
    original_content_tag_enabled: bool = False
    all_original_content: bool = False
    restrict_posting: bool = False
    restrict_commenting: bool = False
    free_form_reports: bool = True
    show_media: bool = False
    accept_followers: bool = False
    link_flair_enabled: bool = False
    link_flair_position: str | None = None
    comment_score_hide_mins: int = 0
    suggested_comment_sort: str | None = None
    advertiser_category: str | None = None
    # Branding
    community_icon: str | None = None
    icon_img: str | None = None
    banner_img: str | None = None
    banner_background_image: str | None = None
    header_img: str | None = None
    header_title: str | None = None
    primary_color: str | None = None
    key_color: str | None = None
    banner_background_color: str | None = None


class RedditUserSubreddit(_BaseModel):
    """The profile subreddit (u/<name>) embedded in a user's ``about`` payload."""

    display_name: str = ""
    display_name_prefixed: str | None = None
    title: str = ""
    public_description: str = ""
    subscribers: int = 0
    url: str = ""
    subreddit_type: str | None = None
    over_18: bool = False
    icon_img: str | None = None
    banner_img: str | None = None
    community_icon: str | None = None
    primary_color: str | None = None


class RedditUser(_BaseModel):
    """A Reddit user account."""

    id: str | None = None
    name: str
    display_name_prefixed: str | None = None
    # Karma
    link_karma: int = 0
    comment_karma: int = 0
    awardee_karma: int = 0
    awarder_karma: int = 0
    total_karma: int = 0
    # Timestamps
    created_utc: float = 0
    created_at: str | None = None
    # Flags
    is_gold: bool = False
    is_employee: bool = False
    is_mod: bool = False
    is_friend: bool = False
    verified: bool = False
    has_verified_email: bool = False
    hide_from_robots: bool = False
    accept_followers: bool = False
    # Avatar
    icon_img: str | None = None
    snoovatar_img: str | None = None
    # Profile subreddit
    subreddit: RedditUserSubreddit | None = None


# =============================================================================
# Reference Models
# =============================================================================


class RedditRule(_BaseModel):
    """A subreddit posting rule."""

    priority: int = 0
    short_name: str = ""
    description: str = ""
    description_html: str | None = None
    violation_reason: str | None = None
    created_utc: float = 0
    kind: str | None = None


class RedditWikiPage(_BaseModel):
    """A subreddit wiki page."""

    title: str = ""
    content_md: str = ""
    content_html: str | None = None
    revision_by: str | None = None
    revision_date: float | None = None
    revision_id: str | None = None
    may_revise: bool = False
    reason: str | None = None


class RedditTrophy(_BaseModel):
    """A Reddit user trophy/award."""

    id: str | None = None
    award_id: str | None = None
    name: str
    description: str | None = None
    icon_url: str | None = None
    icon_40: str | None = None
    icon_70: str | None = None
    url: str | None = None
    granted_at: float | None = None


class RedditModeratedSubreddit(_BaseModel):
    """A subreddit a user moderates (from ``/user/{u}/moderated_subreddits``)."""

    fullname: str | None = None
    sr: str | None = None
    name: str = ""
    display_name_prefixed: str | None = None
    sr_display_name_prefixed: str | None = None
    title: str = ""
    url: str = ""
    subscribers: int = 0
    subreddit_type: str | None = None
    over_18: bool = False
    community_icon: str | None = None
    icon_img: str | None = None
    banner_img: str | None = None
    primary_color: str | None = None
    key_color: str | None = None
    created_utc: float = 0
    created_at: str | None = None
    mod_permissions: list[str] = Field(default_factory=list)


# =============================================================================
# Pagination
# =============================================================================


class RedditPagination(_BaseModel):
    """Pagination cursor metadata.

    Attributes:
        after: Cursor for the next page.
        before: Cursor for the previous page.
        count: Number of items returned.
        limit: Page size requested.
    """

    after: str | None = None
    before: str | None = None
    count: int = 0
    limit: int = 25


# =============================================================================
# Response Envelopes
# =============================================================================


class SearchPostsResponse(_BaseModel):
    """Response from the Reddit post search endpoint.

    Attributes:
        posts: List of matching posts.
        after: Pagination cursor for the next page.
        before: Pagination cursor for the previous page.
        count: Total number of results returned.
    """

    posts: list[RedditPost] = Field(default_factory=list)
    after: str | None = None
    before: str | None = None
    count: int = 0


class SubredditPostsResponse(_BaseModel):
    """Response from the subreddit posts endpoint.

    Attributes:
        posts: List of posts from the subreddit.
        after: Pagination cursor for the next page.
        before: Pagination cursor for the previous page.
        count: Number of posts returned.
        subreddit: Subreddit name the posts belong to.
    """

    posts: list[RedditPost] = Field(default_factory=list)
    after: str | None = None
    before: str | None = None
    count: int = 0
    subreddit: str = ""


class PostDetailResponse(_BaseModel):
    """Response from the post detail endpoint.

    Attributes:
        post: The full post data.
    """

    post: RedditPost | None = None


class PostCommentsResponse(_BaseModel):
    """Response from the post comments endpoint.

    Attributes:
        comments: List of comments.
        post: The parent post.
        after: Pagination cursor for the next page.
        count: Number of comments returned.
    """

    comments: list[RedditComment] = Field(default_factory=list)
    post: RedditPost | None = None
    after: str | None = None
    count: int = 0


class PostDuplicatesResponse(_BaseModel):
    """Response from the post duplicates endpoint.

    Attributes:
        posts: List of duplicate/cross-posted posts.
        after: Pagination cursor for the next page.
        count: Number of duplicates returned.
    """

    posts: list[RedditPost] = Field(default_factory=list)
    after: str | None = None
    count: int = 0


class TrendingPostsResponse(_BaseModel):
    """Response from the trending posts endpoint.

    Attributes:
        posts: List of trending posts.
        after: Pagination cursor for the next page.
        count: Number of posts returned.
    """

    posts: list[RedditPost] = Field(default_factory=list)
    after: str | None = None
    count: int = 0


class UserProfileResponse(_BaseModel):
    """Response from the user profile endpoint.

    Attributes:
        user: The user profile data.
    """

    user: RedditUser | None = None


class UserPostsResponse(_BaseModel):
    """Response from the user posts endpoint.

    Attributes:
        posts: List of posts submitted by the user.
        after: Pagination cursor for the next page.
        count: Number of posts returned.
    """

    posts: list[RedditPost] = Field(default_factory=list)
    after: str | None = None
    count: int = 0


class UserCommentsResponse(_BaseModel):
    """Response from the user comments endpoint.

    Attributes:
        comments: List of comments made by the user.
        after: Pagination cursor for the next page.
        count: Number of comments returned.
    """

    comments: list[RedditComment] = Field(default_factory=list)
    after: str | None = None
    count: int = 0


class UserModeratedResponse(_BaseModel):
    """Response from the user moderated subreddits endpoint.

    Attributes:
        subreddits: List of subreddits the user moderates.
    """

    subreddits: list[RedditModeratedSubreddit] = Field(default_factory=list)


class UserTrophiesResponse(_BaseModel):
    """Response from the user trophies endpoint.

    Attributes:
        trophies: List of trophies awarded to the user.
    """

    trophies: list[RedditTrophy] = Field(default_factory=list)


class SubredditsListResponse(_BaseModel):
    """Response from a subreddit listing endpoint (popular, new, search).

    Attributes:
        subreddits: List of subreddits.
        after: Pagination cursor for the next page.
        count: Number of subreddits returned.
    """

    subreddits: list[RedditSubreddit] = Field(default_factory=list)
    after: str | None = None
    count: int = 0


class SubredditDetailResponse(_BaseModel):
    """Response from the subreddit detail endpoint.

    Attributes:
        subreddit: The subreddit data.
    """

    subreddit: RedditSubreddit | None = None


class SubredditRulesResponse(_BaseModel):
    """Response from the subreddit rules endpoint.

    Attributes:
        rules: List of subreddit rules.
        subreddit: Subreddit name.
        site_rules: Reddit site-wide rules that also apply.
    """

    rules: list[RedditRule] = Field(default_factory=list)
    subreddit: str = ""
    site_rules: list[str] = Field(default_factory=list)


class SubredditWikiPagesResponse(_BaseModel):
    """Response from the subreddit wiki pages list endpoint.

    Attributes:
        pages: List of wiki page names.
        subreddit: Subreddit name.
    """

    pages: list[str] = Field(default_factory=list)
    subreddit: str = ""


class SubredditWikiPageResponse(_BaseModel):
    """Response from the subreddit wiki page endpoint.

    Attributes:
        page: The wiki page content.
        subreddit: Subreddit name.
    """

    page: RedditWikiPage | None = None
    subreddit: str = ""


class SearchUsersResponse(_BaseModel):
    """Response from the user search endpoint.

    Attributes:
        users: List of matching users.
        after: Pagination cursor for the next page.
        count: Number of users returned.
    """

    users: list[RedditUser] = Field(default_factory=list)
    after: str | None = None
    count: int = 0
