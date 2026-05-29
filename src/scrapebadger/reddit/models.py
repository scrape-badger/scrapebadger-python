"""Pydantic models for Reddit API responses.

This module contains all the data models used by the Reddit API client.
All models are immutable (frozen) and use strict validation for type safety.

Models are organised into:
- Core models: RedditPost, RedditComment, RedditSubreddit, RedditUser
- Reference models: RedditRule, RedditWikiPage, RedditTrophy
- Response envelopes: SearchPostsResponse, SubredditPostsResponse, etc.

Note: As of 0.9.0, Reddit response models are trimmed to the fields available
via the old.reddit.com HTML/RSS source after Reddit deprecated the
unauthenticated .json API.
"""

from __future__ import annotations

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
# Core Models
# =============================================================================


class RedditPost(_BaseModel):
    """A Reddit post (submission).

    Field names match the canonical backend model exactly so that API responses
    can be passed through ``model_validate`` without any mapping layer.

    Attributes:
        id: Post ID (base-36, e.g. "abc123").
        fullname: Fully-qualified Reddit name ("t3_abc123").
        title: Post title.
        selftext: Body text for self posts.
        selftext_html: HTML-rendered body text.
        url: Canonical URL of the linked resource or post.
        permalink: Relative Reddit URL path.
        domain: Domain of the linked URL (or "self.<subreddit>").
        author: Username of the post author.
        author_fullname: Author's fully-qualified Reddit name.
        subreddit: Subreddit name (without r/ prefix).
        subreddit_id: Subreddit fullname (e.g. "t5_2qh0y").
        subreddit_name_prefixed: Subreddit name with prefix ("r/python").
        subreddit_type: Subreddit visibility ("public", "restricted", "private").
        score: Net upvotes.
        num_comments: Number of top-level comments.
        num_crossposts: Number of times crossposted.
        created_utc: UTC epoch timestamp of post creation.
        created_at: ISO 8601 UTC string of post creation (human-readable).
        is_self: Whether this is a self (text) post.
        is_gallery: Whether the post is an image gallery.
        is_nsfw: Whether the post is marked NSFW.
        is_spoiler: Whether the post is marked as a spoiler.
        is_stickied: Whether the post is stickied in its subreddit.
        is_original_content: Whether the post is marked as OC.
        link_flair_text: Post flair display text.
        gilded: Number of times gilded.
    """

    id: str
    fullname: str = ""
    title: str
    selftext: str = ""
    selftext_html: str | None = None
    url: str = ""
    permalink: str = ""
    domain: str = ""
    author: str = ""
    author_fullname: str | None = None
    subreddit: str = ""
    subreddit_id: str | None = None
    subreddit_name_prefixed: str | None = None
    subreddit_type: str | None = None
    score: int = 0
    num_comments: int = 0
    num_crossposts: int = 0
    created_utc: float = 0
    created_at: str | None = None
    is_self: bool = False
    is_gallery: bool = False
    is_nsfw: bool = False
    is_spoiler: bool = False
    is_stickied: bool = False
    is_original_content: bool = False
    link_flair_text: str | None = None
    gilded: int = 0


class RedditComment(_BaseModel):
    """A Reddit comment.

    Attributes:
        id: Comment ID (base-36 string).
        fullname: Fully-qualified Reddit name ("t1_<id>").
        body: Comment text body (markdown).
        body_html: HTML-rendered comment body.
        author: Username of the comment author.
        author_fullname: Author's fully-qualified Reddit name.
        subreddit: Subreddit the comment belongs to.
        subreddit_id: Subreddit fullname (e.g. "t5_2qh0y").
        subreddit_name_prefixed: Subreddit name with prefix ("r/python").
        post_id: ID of the parent post.
        permalink: Relative Reddit URL path to the comment.
        score: Net upvotes.
        depth: Nesting depth in the comment tree (0 = top-level).
        created_utc: UTC epoch timestamp of comment creation.
        created_at: ISO 8601 UTC string of comment creation.
        is_stickied: Whether the comment is stickied.
        replies: Nested replies (populated for threaded responses).
    """

    id: str
    fullname: str = ""
    body: str = ""
    body_html: str | None = None
    author: str = ""
    author_fullname: str | None = None
    subreddit: str = ""
    subreddit_id: str | None = None
    subreddit_name_prefixed: str | None = None
    post_id: str | None = None
    permalink: str = ""
    score: int = 0
    depth: int = 0
    created_utc: float = 0
    created_at: str | None = None
    is_stickied: bool = False
    replies: list[RedditComment] = Field(default_factory=list)


class RedditSubreddit(_BaseModel):
    """A Reddit subreddit (community).

    Attributes:
        id: Subreddit ID (base-36).
        fullname: Fully-qualified Reddit name ("t5_<id>").
        name: Subreddit name (without r/ prefix).
        display_name_prefixed: Name with prefix ("r/python").
        title: Subreddit headline shown in the header.
        description: Full sidebar description (markdown).
        public_description: Short public description shown in listings.
        url: Relative URL path (e.g. "/r/python/").
        created_utc: UTC epoch timestamp of subreddit creation.
        created_at: ISO 8601 UTC string of subreddit creation.
        is_nsfw: Whether the subreddit is NSFW.
    """

    id: str
    fullname: str = ""
    name: str
    display_name_prefixed: str | None = None
    title: str = ""
    description: str = ""
    public_description: str = ""
    url: str = ""
    created_utc: float = 0
    created_at: str | None = None
    is_nsfw: bool = False


class RedditUser(_BaseModel):
    """A Reddit user account.

    Attributes:
        name: Username.
        display_name_prefixed: Username with prefix ("u/redditor42").
        link_karma: Post karma.
        comment_karma: Comment karma.
        total_karma: Total karma across all categories.
        created_utc: UTC epoch timestamp of account creation.
        created_at: ISO 8601 UTC string of account creation.
        is_gold: Whether the user has Reddit Premium.
    """

    name: str
    display_name_prefixed: str | None = None
    link_karma: int = 0
    comment_karma: int = 0
    total_karma: int = 0
    created_utc: float = 0
    created_at: str | None = None
    is_gold: bool = False


# =============================================================================
# Reference Models
# =============================================================================


class RedditRule(_BaseModel):
    """A subreddit posting rule.

    Attributes:
        priority: Display order (lower = higher priority).
        short_name: Short rule name shown in the sidebar.
        description: Full rule description (may include markdown).
    """

    priority: int = 0
    short_name: str = ""
    description: str = ""


class RedditWikiPage(_BaseModel):
    """A subreddit wiki page.

    Attributes:
        title: Page title.
        content_md: Wiki content as markdown.
        content_html: Wiki content as HTML.
        revision_by: Username of the last editor.
        revision_date: UTC epoch timestamp of the last revision.
    """

    title: str = ""
    content_md: str = ""
    content_html: str | None = None
    revision_by: str | None = None
    revision_date: float | None = None


class RedditTrophy(_BaseModel):
    """A Reddit user trophy/award.

    Attributes:
        name: Trophy name.
        description: Trophy description.
        icon_url: Trophy icon image URL.
        url: URL associated with the trophy (may be None).
    """

    name: str
    description: str | None = None
    icon_url: str | None = None
    url: str | None = None


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

    subreddits: list[RedditSubreddit] = Field(default_factory=list)


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
    """

    rules: list[RedditRule] = Field(default_factory=list)
    subreddit: str = ""


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
