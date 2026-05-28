"""Pydantic models for Reddit API responses.

This module contains all the data models used by the Reddit API client.
All models are immutable (frozen) and use strict validation for type safety.

Models are organised into:
- Nested models: RedditPreviewImage, RedditMedia, RedditAward, RedditUserSummary
- Core models: RedditPost, RedditComment, RedditSubreddit, RedditUser
- Reference models: RedditRule, RedditWikiPage, RedditTrophy
- Response envelopes: SearchPostsResponse, SubredditPostsResponse, etc.
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
# Nested / Reference Models
# =============================================================================


class RedditPreviewImage(_BaseModel):
    """A single image in a post preview set.

    Attributes:
        url: Direct image URL.
        width: Image width in pixels.
        height: Image height in pixels.
    """

    url: str
    width: int
    height: int


class RedditMedia(_BaseModel):
    """Embedded media metadata for a post.

    Attributes:
        type: Media type string (e.g. "youtube.com").
        url: Direct media URL.
        thumbnail_url: Thumbnail image URL.
        width: Media width in pixels.
        height: Media height in pixels.
    """

    type: str | None = None
    url: str | None = None
    thumbnail_url: str | None = None
    width: int | None = None
    height: int | None = None


class RedditAward(_BaseModel):
    """A Reddit award attached to a post or comment.

    Attributes:
        id: Award identifier.
        name: Award display name.
        count: Number of times this award was given.
        icon_url: Award icon image URL.
    """

    id: str | None = None
    name: str
    count: int = 1
    icon_url: str | None = None


class RedditUserSummary(_BaseModel):
    """Compact user reference embedded in other objects.

    Attributes:
        name: Username.
        id: User fullname (e.g. "t2_abc").
        icon_url: Profile icon image URL.
        link_karma: Post karma.
        comment_karma: Comment karma.
        created_utc: UTC epoch timestamp of account creation.
    """

    name: str
    id: str | None = None
    icon_url: str | None = None
    link_karma: int = 0
    comment_karma: int = 0
    created_utc: float | None = None


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
        author_flair_text: Author's flair text in the subreddit.
        author_flair_type: Author's flair type ("text" or "richtext").
        author_flair_template_id: UUID of the author's flair template.
        subreddit: Subreddit name (without r/ prefix).
        subreddit_id: Subreddit fullname (e.g. "t5_2qh0y").
        subreddit_name_prefixed: Subreddit name with prefix ("r/python").
        subreddit_type: Subreddit visibility ("public", "restricted", "private").
        subreddit_subscribers: Number of subreddit subscribers.
        score: Net upvotes.
        ups: Raw upvote count.
        downs: Raw downvote count.
        upvote_ratio: Fraction of upvotes (0.0-1.0).
        num_comments: Number of top-level comments.
        num_crossposts: Number of times crossposted.
        num_duplicates: Number of duplicate/crosspost links.
        view_count: View count (may be None if not available).
        created_utc: UTC epoch timestamp of post creation.
        created_at: ISO 8601 UTC string of post creation (human-readable).
        edited: UTC epoch of last edit, or False if never edited.
        edited_at: ISO 8601 UTC string of last edit.
        is_self: Whether this is a self (text) post.
        is_video: Whether the post contains a video.
        is_gallery: Whether the post is an image gallery.
        is_nsfw: Whether the post is marked NSFW.
        is_spoiler: Whether the post is marked as a spoiler.
        is_locked: Whether comments are locked.
        is_stickied: Whether the post is stickied in its subreddit.
        is_archived: Whether the post is archived (no new votes/comments).
        is_pinned: Whether the post is pinned by a moderator.
        is_original_content: Whether the post is marked as OC.
        is_robot_indexable: Whether the post can be indexed by search engines.
        is_meta: Whether the post is a meta post about the subreddit.
        is_crosspostable: Whether the post can be crossposted.
        send_replies: Whether the author receives inbox replies.
        link_flair_text: Post flair display text.
        link_flair_background_color: Post flair background colour (hex).
        link_flair_text_color: Post flair text colour ("light" or "dark").
        link_flair_template_id: UUID of the post flair template.
        link_flair_type: Post flair type ("text" or "richtext").
        link_flair_css_class: CSS class for the post flair.
        distinguished: Distinguishment type ("moderator", "admin", or None).
        thumbnail: Thumbnail URL or keyword ("self", "default", etc.).
        thumbnail_width: Thumbnail width in pixels.
        thumbnail_height: Thumbnail height in pixels.
        post_hint: Hint about post type ("image", "link", "rich:video", etc.).
        preview_images: List of preview images.
        media: Embedded media metadata.
        gallery_data: Raw gallery item list for gallery posts.
        crosspost_parent: Fullname of the original crossposted post.
        suggested_sort: Moderator-suggested comment sort order.
        total_awards: Total number of awards received.
        awards: List of individual award objects.
        gilded: Number of times gilded.
        content_categories: Content category tags.
        removed_by_category: Removal reason category if removed.
        treatment_tags: A/B test treatment tags.
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
    author_flair_text: str | None = None
    author_flair_type: str | None = None
    author_flair_template_id: str | None = None
    subreddit: str = ""
    subreddit_id: str | None = None
    subreddit_name_prefixed: str | None = None
    subreddit_type: str | None = None
    subreddit_subscribers: int | None = None
    score: int = 0
    ups: int = 0
    downs: int = 0
    upvote_ratio: float | None = None
    num_comments: int = 0
    num_crossposts: int = 0
    num_duplicates: int | None = None
    view_count: int | None = None
    created_utc: float = 0
    created_at: str | None = None
    edited: float | bool | None = None
    edited_at: str | None = None
    is_self: bool = False
    is_video: bool = False
    is_gallery: bool = False
    is_nsfw: bool = False
    is_spoiler: bool = False
    is_locked: bool = False
    is_stickied: bool = False
    is_archived: bool = False
    is_pinned: bool = False
    is_original_content: bool = False
    is_robot_indexable: bool = True
    is_meta: bool = False
    is_crosspostable: bool = False
    send_replies: bool = False
    link_flair_text: str | None = None
    link_flair_background_color: str | None = None
    link_flair_text_color: str | None = None
    link_flair_template_id: str | None = None
    link_flair_type: str | None = None
    link_flair_css_class: str | None = None
    distinguished: str | None = None
    thumbnail: str | None = None
    thumbnail_width: int | None = None
    thumbnail_height: int | None = None
    post_hint: str | None = None
    preview_images: list[RedditPreviewImage] = Field(default_factory=list)
    media: RedditMedia | None = None
    gallery_data: list[dict[str, Any]] | None = None
    crosspost_parent: str | None = None
    suggested_sort: str | None = None
    total_awards: int = 0
    awards: list[RedditAward] = Field(default_factory=list)
    gilded: int = 0
    content_categories: list[str] | None = None
    removed_by_category: str | None = None
    treatment_tags: list[str] = Field(default_factory=list)


class RedditComment(_BaseModel):
    """A Reddit comment.

    Attributes:
        id: Comment ID (base-36 string).
        fullname: Fully-qualified Reddit name ("t1_<id>").
        body: Comment text body (markdown).
        body_html: HTML-rendered comment body.
        author: Username of the comment author.
        author_fullname: Author's fully-qualified Reddit name.
        author_flair_text: Author's flair text in the subreddit.
        author_flair_type: Author's flair type ("text" or "richtext").
        subreddit: Subreddit the comment belongs to.
        subreddit_id: Subreddit fullname (e.g. "t5_2qh0y").
        subreddit_name_prefixed: Subreddit name with prefix ("r/python").
        subreddit_type: Subreddit visibility type.
        post_id: ID of the parent post.
        post_title: Title of the parent post.
        parent_id: Fullname of the parent (t3_ for post, t1_ for comment).
        permalink: Relative Reddit URL path to the comment.
        score: Net upvotes.
        ups: Raw upvote count.
        downs: Raw downvote count.
        controversiality: Controversiality score (0 or 1).
        depth: Nesting depth in the comment tree (0 = top-level).
        created_utc: UTC epoch timestamp of comment creation.
        created_at: ISO 8601 UTC string of comment creation.
        edited: UTC epoch of last edit, or False if never edited.
        edited_at: ISO 8601 UTC string of last edit.
        is_submitter: Whether the commenter is also the post author.
        is_stickied: Whether the comment is stickied.
        is_locked: Whether the comment thread is locked.
        is_score_hidden: Whether the comment score is hidden.
        send_replies: Whether the author receives inbox replies.
        distinguished: Distinguishment type ("moderator", "admin", or None).
        total_awards: Total number of awards received.
        gilded: Number of times gilded.
        replies: Nested replies (populated for threaded responses).
    """

    id: str
    fullname: str = ""
    body: str = ""
    body_html: str | None = None
    author: str = ""
    author_fullname: str | None = None
    author_flair_text: str | None = None
    author_flair_type: str | None = None
    subreddit: str = ""
    subreddit_id: str | None = None
    subreddit_name_prefixed: str | None = None
    subreddit_type: str | None = None
    post_id: str | None = None
    post_title: str | None = None
    parent_id: str | None = None
    permalink: str = ""
    score: int = 0
    ups: int = 0
    downs: int = 0
    controversiality: int = 0
    depth: int = 0
    created_utc: float = 0
    created_at: str | None = None
    edited: float | bool | None = None
    edited_at: str | None = None
    is_submitter: bool = False
    is_stickied: bool = False
    is_locked: bool = False
    is_score_hidden: bool = False
    send_replies: bool = False
    distinguished: str | None = None
    total_awards: int = 0
    gilded: int = 0
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
        description_html: HTML-rendered sidebar description.
        public_description: Short public description shown in listings.
        public_description_html: HTML-rendered short description.
        submit_text: Text shown on the submit page.
        submit_text_html: HTML-rendered submit text.
        header_title: Text shown below the subreddit header image.
        url: Relative URL path (e.g. "/r/python/").
        type: Subreddit visibility ("public", "restricted", "private").
        submission_type: Allowed submission types ("any", "link", "self").
        subscribers: Number of subscribers.
        active_users: Current active (online) users.
        created_utc: UTC epoch timestamp of subreddit creation.
        created_at: ISO 8601 UTC string of subreddit creation.
        is_nsfw: Whether the subreddit is NSFW.
        is_quarantined: Whether the subreddit is quarantined.
        is_advertiser_friendly: Whether the subreddit is advertiser-friendly.
        advertiser_category: Advertiser category classification.
        language: Primary language code.
        icon_url: Subreddit icon image URL.
        header_url: Subreddit header image URL.
        banner_url: Subreddit banner image URL.
        banner_background_color: Banner background colour (hex).
        primary_color: Primary brand colour (hex).
        key_color: Key accent colour (hex).
        wiki_enabled: Whether the wiki is enabled.
        allow_images: Whether image posts are allowed.
        allow_videos: Whether video posts are allowed.
        allow_galleries: Whether gallery posts are allowed.
        allow_polls: Whether poll posts are allowed.
        allow_discovery: Whether the subreddit appears in discovery feeds.
        spoilers_enabled: Whether spoiler tags are enabled.
        emojis_enabled: Whether custom emojis are enabled.
        free_form_reports: Whether free-form report reasons are enabled.
        accept_followers: Whether users can follow the subreddit.
        restrict_posting: Whether posting is restricted to approved users.
        link_flair_enabled: Whether post flair is enabled.
        link_flair_position: Position of post flair ("left" or "right").
        user_flair_enabled: Whether user flair is enabled.
        user_flair_position: Position of user flair ("left" or "right").
        comment_score_hide_mins: Minutes after which comment scores are hidden.
        should_archive_posts: Whether posts are archived after 6 months.
        allowed_media_in_comments: Allowed media types in comments.
    """

    id: str
    fullname: str = ""
    name: str
    display_name_prefixed: str | None = None
    title: str = ""
    description: str = ""
    description_html: str | None = None
    public_description: str = ""
    public_description_html: str | None = None
    submit_text: str = ""
    submit_text_html: str | None = None
    header_title: str | None = None
    url: str = ""
    type: str = "public"
    submission_type: str | None = None
    subscribers: int = 0
    active_users: int | None = None
    created_utc: float = 0
    created_at: str | None = None
    is_nsfw: bool = False
    is_quarantined: bool = False
    is_advertiser_friendly: bool = True
    advertiser_category: str | None = None
    language: str | None = None
    icon_url: str | None = None
    header_url: str | None = None
    banner_url: str | None = None
    banner_background_color: str | None = None
    primary_color: str | None = None
    key_color: str | None = None
    wiki_enabled: bool = False
    allow_images: bool = True
    allow_videos: bool = True
    allow_galleries: bool = False
    allow_polls: bool = False
    allow_discovery: bool = True
    spoilers_enabled: bool = False
    emojis_enabled: bool = False
    free_form_reports: bool = True
    accept_followers: bool = True
    restrict_posting: bool = False
    link_flair_enabled: bool = False
    link_flair_position: str | None = None
    user_flair_enabled: bool = False
    user_flair_position: str | None = None
    comment_score_hide_mins: int = 0
    should_archive_posts: bool = False
    allowed_media_in_comments: list[str] = Field(default_factory=list)


class RedditUser(_BaseModel):
    """A Reddit user account.

    Attributes:
        id: User ID (base-36).
        fullname: Fully-qualified Reddit name ("t2_<id>").
        name: Username.
        display_name_prefixed: Username with prefix ("u/redditor42").
        icon_url: Profile icon image URL.
        snoovatar_url: Snoovatar (animated avatar) image URL.
        banner_url: Profile banner image URL.
        profile_title: Profile page title/tagline.
        profile_url: Profile page URL.
        description: About/bio text.
        link_karma: Post karma.
        comment_karma: Comment karma.
        awardee_karma: Karma from received awards.
        awarder_karma: Karma from given awards.
        total_karma: Total karma across all categories.
        created_utc: UTC epoch timestamp of account creation.
        created_at: ISO 8601 UTC string of account creation.
        has_verified_email: Whether the user's email is verified.
        verified: Whether the user account is verified (legacy field).
        accepts_followers: Whether the user can be followed.
        has_subscribed: Whether the user has subscribed to Reddit Premium.
        is_employee: Whether the user is a Reddit employee.
        is_mod: Whether the user is a moderator of any subreddit.
        is_gold: Whether the user has Reddit Premium.
        is_suspended: Whether the user account is suspended.
        is_nsfw: Whether the user's profile is marked NSFW.
        pref_show_snoovatar: Whether the user prefers to show their snoovatar.
    """

    id: str
    fullname: str | None = None
    name: str
    display_name_prefixed: str | None = None
    icon_url: str | None = None
    snoovatar_url: str | None = None
    banner_url: str | None = None
    profile_title: str | None = None
    profile_url: str | None = None
    description: str = ""
    link_karma: int = 0
    comment_karma: int = 0
    awardee_karma: int = 0
    awarder_karma: int = 0
    total_karma: int = 0
    created_utc: float = 0
    created_at: str | None = None
    has_verified_email: bool = False
    verified: bool = False
    accepts_followers: bool = False
    has_subscribed: bool = False
    is_employee: bool = False
    is_mod: bool = False
    is_gold: bool = False
    is_suspended: bool = False
    is_nsfw: bool = False
    pref_show_snoovatar: bool = False


# =============================================================================
# Reference Models
# =============================================================================


class RedditRule(_BaseModel):
    """A subreddit posting rule.

    Attributes:
        short_name: Short rule name shown in the sidebar.
        description: Full rule description (may include markdown).
        description_html: HTML-rendered rule description.
        kind: Rule kind ("link", "comment", or "all").
        priority: Display order (lower = higher priority).
        violation_reason: Short reason string used in reports.
    """

    short_name: str = ""
    description: str = ""
    description_html: str | None = None
    kind: str = "all"
    priority: int = 0
    violation_reason: str | None = None


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
