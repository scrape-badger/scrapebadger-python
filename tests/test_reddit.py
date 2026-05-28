"""Unit tests for Reddit SDK methods and models.

Tests are organised into:
- TestRedditModels: Pydantic model construction, validation, and immutability
- TestRedditClient: RedditClient sub-client wiring
- TestSearchClient: Search endpoint via mocked HTTP client
- TestPostsClient: Posts endpoints via mocked HTTP client
- TestSubredditsClient: Subreddits endpoints via mocked HTTP client
- TestUsersClient: User endpoints via mocked HTTP client
- TestRedditImports: Public API importability
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from scrapebadger.reddit.client import RedditClient
from scrapebadger.reddit.models import (
    PostCommentsResponse,
    PostDetailResponse,
    PostDuplicatesResponse,
    RedditAward,
    RedditComment,
    RedditMedia,
    RedditPost,
    RedditPreviewImage,
    RedditRule,
    RedditSubreddit,
    RedditTrophy,
    RedditUser,
    RedditUserSummary,
    RedditWikiPage,
    SearchPostsResponse,
    SubredditPostsResponse,
    SubredditRulesResponse,
    SubredditsListResponse,
    SubredditWikiPageResponse,
    SubredditWikiPagesResponse,
    TrendingPostsResponse,
    UserCommentsResponse,
    UserModeratedResponse,
    UserPostsResponse,
    UserProfileResponse,
    UserTrophiesResponse,
)
from scrapebadger.reddit.posts import PostsClient
from scrapebadger.reddit.search import SearchClient
from scrapebadger.reddit.subreddits import SubredditsClient
from scrapebadger.reddit.users import UsersClient

# ---------------------------------------------------------------------------
# Shared sample data — field names match the canonical backend model exactly
# ---------------------------------------------------------------------------

SAMPLE_POST: dict[str, Any] = {
    "id": "abc123",
    "fullname": "t3_abc123",
    "title": "Hello Reddit",
    "selftext": "This is the post body",
    "selftext_html": "<p>This is the post body</p>",
    "url": "https://www.reddit.com/r/python/comments/abc123/hello_reddit/",
    "permalink": "/r/python/comments/abc123/hello_reddit/",
    "domain": "self.python",
    "author": "user42",
    "author_fullname": "t2_user42",
    "author_flair_text": "Python Dev",
    "author_flair_type": "text",
    "author_flair_template_id": "aaaaaaaa-0000-0000-0000-000000000000",
    "subreddit": "python",
    "subreddit_id": "t5_2qh0y",
    "subreddit_name_prefixed": "r/python",
    "subreddit_type": "public",
    "subreddit_subscribers": 1500000,
    "score": 1234,
    "ups": 1300,
    "downs": 66,
    "upvote_ratio": 0.97,
    "num_comments": 56,
    "num_crossposts": 3,
    "num_duplicates": 2,
    "view_count": 9876,
    "created_utc": 1700000000.0,
    "created_at": "2023-11-14T22:13:20+00:00",
    "edited": False,
    "edited_at": None,
    "is_self": True,
    "is_video": False,
    "is_gallery": False,
    "is_nsfw": False,
    "is_spoiler": False,
    "is_locked": False,
    "is_stickied": False,
    "is_archived": False,
    "is_pinned": False,
    "is_original_content": True,
    "is_robot_indexable": True,
    "is_meta": False,
    "is_crosspostable": True,
    "send_replies": True,
    "link_flair_text": "Discussion",
    "link_flair_background_color": "#ff4500",
    "link_flair_text_color": "light",
    "link_flair_template_id": "bbbbbbbb-0000-0000-0000-000000000000",
    "link_flair_type": "text",
    "link_flair_css_class": "discussion",
    "distinguished": None,
    "thumbnail": "self",
    "thumbnail_width": 140,
    "thumbnail_height": 105,
    "post_hint": None,
    "preview_images": [{"url": "https://preview.redd.it/img.jpg", "width": 640, "height": 480}],
    "media": None,
    "gallery_data": None,
    "crosspost_parent": None,
    "suggested_sort": "top",
    "total_awards": 2,
    "awards": [{"name": "Helpful", "count": 1, "icon_url": "https://icon.url/helpful.png"}],
    "gilded": 0,
    "content_categories": None,
    "removed_by_category": None,
    "treatment_tags": ["tag_a", "tag_b"],
}

SAMPLE_COMMENT: dict[str, Any] = {
    "id": "cmt001",
    "fullname": "t1_cmt001",
    "body": "Great post!",
    "body_html": "<p>Great post!</p>",
    "author": "commenter1",
    "author_fullname": "t2_commenter1",
    "author_flair_text": None,
    "author_flair_type": "text",
    "subreddit": "python",
    "subreddit_id": "t5_2qh0y",
    "subreddit_name_prefixed": "r/python",
    "subreddit_type": "public",
    "post_id": "abc123",
    "post_title": "Hello Reddit",
    "parent_id": "t3_abc123",
    "permalink": "/r/python/comments/abc123/hello_reddit/cmt001/",
    "score": 42,
    "ups": 45,
    "downs": 3,
    "controversiality": 0,
    "depth": 0,
    "created_utc": 1700001000.0,
    "created_at": "2023-11-14T22:30:00+00:00",
    "edited": False,
    "edited_at": None,
    "is_submitter": False,
    "is_stickied": False,
    "is_locked": False,
    "is_score_hidden": False,
    "send_replies": True,
    "distinguished": None,
    "total_awards": 0,
    "gilded": 0,
    "replies": [],
}

SAMPLE_SUBREDDIT: dict[str, Any] = {
    "id": "2qh0y",
    "fullname": "t5_2qh0y",
    "name": "python",
    "display_name_prefixed": "r/python",
    "title": "Python - The programming language",
    "description": "News about the dynamic, interpreted programming language Python",
    "description_html": "<p>News about the dynamic, interpreted programming language Python</p>",
    "public_description": "Python news",
    "public_description_html": "<p>Python news</p>",
    "submit_text": "Submit a post",
    "submit_text_html": "<p>Submit a post</p>",
    "header_title": "Python",
    "url": "/r/python/",
    "type": "public",
    "submission_type": "any",
    "subscribers": 1500000,
    "active_users": 3200,
    "created_utc": 1200000000.0,
    "created_at": "2008-01-11T00:00:00+00:00",
    "is_nsfw": False,
    "is_quarantined": False,
    "is_advertiser_friendly": True,
    "advertiser_category": "Technology",
    "language": "en",
    "icon_url": "https://styles.redditmedia.com/icon.png",
    "header_url": None,
    "banner_url": None,
    "banner_background_color": "#ffffff",
    "primary_color": "#ff4500",
    "key_color": "#ff4500",
    "wiki_enabled": True,
    "allow_images": True,
    "allow_videos": False,
    "allow_galleries": True,
    "allow_polls": False,
    "allow_discovery": True,
    "spoilers_enabled": True,
    "emojis_enabled": False,
    "free_form_reports": True,
    "accept_followers": True,
    "restrict_posting": False,
    "link_flair_enabled": True,
    "link_flair_position": "left",
    "user_flair_enabled": True,
    "user_flair_position": "right",
    "comment_score_hide_mins": 60,
    "should_archive_posts": True,
    "allowed_media_in_comments": ["gif", "image"],
}

SAMPLE_USER: dict[str, Any] = {
    "id": "usr001",
    "fullname": "t2_usr001",
    "name": "redditor42",
    "display_name_prefixed": "u/redditor42",
    "icon_url": "https://www.redditstatic.com/avatars/avatar.png",
    "snoovatar_url": "https://www.redditstatic.com/snoovatar/avatar.png",
    "banner_url": None,
    "profile_title": "All about Python",
    "profile_url": "/user/redditor42/",
    "description": "Python enthusiast",
    "link_karma": 5000,
    "comment_karma": 12000,
    "awardee_karma": 100,
    "awarder_karma": 50,
    "total_karma": 17150,
    "created_utc": 1400000000.0,
    "created_at": "2014-05-13T16:53:20+00:00",
    "has_verified_email": True,
    "verified": True,
    "accepts_followers": True,
    "has_subscribed": False,
    "is_employee": False,
    "is_mod": True,
    "is_gold": False,
    "is_suspended": False,
    "is_nsfw": False,
    "pref_show_snoovatar": True,
}

SAMPLE_RULE: dict[str, Any] = {
    "short_name": "Be nice",
    "description": "Treat others with respect",
    "description_html": "<p>Treat others with respect</p>",
    "kind": "all",
    "priority": 1,
    "violation_reason": "Being mean",
}

SAMPLE_WIKI_PAGE: dict[str, Any] = {
    "title": "rules",
    "content_md": "# Rules\n\n- Be nice",
    "content_html": "<h1>Rules</h1><ul><li>Be nice</li></ul>",
    "revision_by": "moderator1",
    "revision_date": 1700000000.0,
}

SAMPLE_TROPHY: dict[str, Any] = {
    "name": "Verified Email",
    "description": "Verified Email",
    "icon_url": "https://www.redditstatic.com/awards/trophies/email.png",
    "url": None,
}

SEARCH_POSTS_RESPONSE: dict[str, Any] = {
    "posts": [SAMPLE_POST],
    "after": "t3_xyz789",
    "before": None,
    "count": 1,
}

SUBREDDIT_POSTS_RESPONSE: dict[str, Any] = {
    "posts": [SAMPLE_POST],
    "after": "t3_xyz789",
    "before": None,
    "count": 1,
    "subreddit": "python",
}

POST_DETAIL_RESPONSE: dict[str, Any] = {
    "post": SAMPLE_POST,
}

POST_COMMENTS_RESPONSE: dict[str, Any] = {
    "comments": [SAMPLE_COMMENT],
    "post": SAMPLE_POST,
    "after": None,
    "count": 1,
}

POST_DUPLICATES_RESPONSE: dict[str, Any] = {
    "posts": [SAMPLE_POST],
    "after": None,
    "count": 1,
}

TRENDING_POSTS_RESPONSE: dict[str, Any] = {
    "posts": [SAMPLE_POST],
    "after": None,
    "count": 1,
}

USER_PROFILE_RESPONSE: dict[str, Any] = {
    "user": SAMPLE_USER,
}

USER_POSTS_RESPONSE: dict[str, Any] = {
    "posts": [SAMPLE_POST],
    "after": None,
    "count": 1,
}

USER_COMMENTS_RESPONSE: dict[str, Any] = {
    "comments": [SAMPLE_COMMENT],
    "after": None,
    "count": 1,
}

USER_MODERATED_RESPONSE: dict[str, Any] = {
    "subreddits": [SAMPLE_SUBREDDIT],
}

USER_TROPHIES_RESPONSE: dict[str, Any] = {
    "trophies": [SAMPLE_TROPHY],
}

SUBREDDITS_LIST_RESPONSE: dict[str, Any] = {
    "subreddits": [SAMPLE_SUBREDDIT],
    "after": None,
    "count": 1,
}

SUBREDDIT_RULES_RESPONSE: dict[str, Any] = {
    "rules": [SAMPLE_RULE],
    "subreddit": "python",
}

SUBREDDIT_WIKI_PAGES_RESPONSE: dict[str, Any] = {
    "pages": ["rules", "faq"],
    "subreddit": "python",
}

SUBREDDIT_WIKI_PAGE_RESPONSE: dict[str, Any] = {
    "page": SAMPLE_WIKI_PAGE,
    "subreddit": "python",
}

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_base_client() -> MagicMock:
    """Return a mock BaseClient with AsyncMock methods."""
    client = MagicMock()
    client.get = AsyncMock()
    client.post = AsyncMock()
    return client


@pytest.fixture
def reddit_client(mock_base_client: MagicMock) -> RedditClient:
    """Return a RedditClient backed by a mock base client."""
    return RedditClient(mock_base_client)


@pytest.fixture
def search_client(mock_base_client: MagicMock) -> SearchClient:
    """Return a SearchClient backed by a mock base client."""
    return SearchClient(mock_base_client)


@pytest.fixture
def posts_client(mock_base_client: MagicMock) -> PostsClient:
    """Return a PostsClient backed by a mock base client."""
    return PostsClient(mock_base_client)


@pytest.fixture
def subreddits_client(mock_base_client: MagicMock) -> SubredditsClient:
    """Return a SubredditsClient backed by a mock base client."""
    return SubredditsClient(mock_base_client)


@pytest.fixture
def users_client(mock_base_client: MagicMock) -> UsersClient:
    """Return a UsersClient backed by a mock base client."""
    return UsersClient(mock_base_client)


# ===========================================================================
# TestRedditModels
# ===========================================================================


class TestRedditModels:
    """Pydantic model construction, validation, and immutability tests."""

    # -- RedditPreviewImage --

    def test_reddit_preview_image(self) -> None:
        img = RedditPreviewImage(url="https://example.com/img.jpg", width=640, height=480)
        assert img.url == "https://example.com/img.jpg"
        assert img.width == 640
        assert img.height == 480

    def test_reddit_preview_image_is_frozen(self) -> None:
        img = RedditPreviewImage(url="https://example.com/img.jpg", width=1, height=1)
        with pytest.raises(Exception):  # noqa: B017
            img.url = "mutated"  # type: ignore[misc]

    # -- RedditMedia --

    def test_reddit_media_full(self) -> None:
        media = RedditMedia(
            type="youtube.com",
            url="https://youtube.com/watch?v=abc",
            thumbnail_url="https://img.youtube.com/thumb.jpg",
            width=1280,
            height=720,
        )
        assert media.type == "youtube.com"
        assert media.width == 1280

    def test_reddit_media_minimal(self) -> None:
        media = RedditMedia()
        assert media.type is None
        assert media.url is None
        assert media.width is None

    # -- RedditAward --

    def test_reddit_award_full(self) -> None:
        award = RedditAward(
            id="award_helpful",
            name="Helpful",
            count=2,
            icon_url="https://icon.url/helpful.png",
        )
        assert award.id == "award_helpful"
        assert award.count == 2

    def test_reddit_award_minimal(self) -> None:
        award = RedditAward(name="Gold")
        assert award.count == 1
        assert award.id is None

    # -- RedditUserSummary --

    def test_reddit_user_summary_full(self) -> None:
        summary = RedditUserSummary(
            name="user42",
            id="t2_user42",
            icon_url="https://icon.url/avatar.png",
            link_karma=100,
            comment_karma=200,
            created_utc=1400000000.0,
        )
        assert summary.name == "user42"
        assert summary.link_karma == 100

    def test_reddit_user_summary_minimal(self) -> None:
        summary = RedditUserSummary(name="user")
        assert summary.link_karma == 0
        assert summary.id is None

    # -- RedditPost --

    def test_reddit_post_full(self) -> None:
        post = RedditPost.model_validate(SAMPLE_POST)
        assert post.id == "abc123"
        assert post.fullname == "t3_abc123"
        assert post.title == "Hello Reddit"
        assert post.author == "user42"
        assert post.author_fullname == "t2_user42"
        assert post.author_flair_text == "Python Dev"
        assert post.author_flair_type == "text"
        assert post.author_flair_template_id == "aaaaaaaa-0000-0000-0000-000000000000"
        assert post.subreddit == "python"
        assert post.subreddit_name_prefixed == "r/python"
        assert post.subreddit_type == "public"
        assert post.subreddit_subscribers == 1500000
        assert post.score == 1234
        assert post.ups == 1300
        assert post.downs == 66
        assert post.upvote_ratio == 0.97
        assert post.num_comments == 56
        assert post.num_crossposts == 3
        assert post.num_duplicates == 2
        assert post.view_count == 9876
        assert post.created_at == "2023-11-14T22:13:20+00:00"
        assert post.is_nsfw is False
        assert post.is_spoiler is False
        assert post.is_locked is False
        assert post.is_stickied is False
        assert post.is_pinned is False
        assert post.is_robot_indexable is True
        assert post.is_meta is False
        assert post.is_crosspostable is True
        assert post.send_replies is True
        assert post.link_flair_text == "Discussion"
        assert post.link_flair_text_color == "light"
        assert post.link_flair_template_id == "bbbbbbbb-0000-0000-0000-000000000000"
        assert post.link_flair_type == "text"
        assert post.link_flair_css_class == "discussion"
        assert post.thumbnail_width == 140
        assert post.thumbnail_height == 105
        assert post.suggested_sort == "top"
        assert post.treatment_tags == ["tag_a", "tag_b"]
        assert len(post.preview_images) == 1
        assert post.preview_images[0].width == 640
        assert len(post.awards) == 1
        assert post.awards[0].name == "Helpful"

    def test_reddit_post_minimal(self) -> None:
        post = RedditPost(id="x1", title="Test")
        assert post.score == 0
        assert post.num_comments == 0
        assert post.selftext == ""
        assert post.link_flair_text is None
        assert post.fullname == ""
        assert post.num_crossposts == 0
        assert post.view_count is None
        assert post.created_at is None
        assert post.is_pinned is False
        assert post.is_robot_indexable is True
        assert post.is_meta is False
        assert post.is_crosspostable is False
        assert post.send_replies is False
        assert post.link_flair_text_color is None
        assert post.link_flair_template_id is None
        assert post.link_flair_type is None
        assert post.link_flair_css_class is None
        assert post.thumbnail_width is None
        assert post.thumbnail_height is None
        assert post.suggested_sort is None
        assert post.treatment_tags == []

    def test_reddit_post_is_frozen(self) -> None:
        post = RedditPost.model_validate(SAMPLE_POST)
        with pytest.raises(Exception):  # noqa: B017
            post.title = "mutated"  # type: ignore[misc]

    def test_reddit_post_extra_fields_ignored(self) -> None:
        data = {**SAMPLE_POST, "unknown_future_field": "value"}
        post = RedditPost.model_validate(data)
        assert post.id == "abc123"

    def test_reddit_post_preview_images_parsed(self) -> None:
        post = RedditPost.model_validate(SAMPLE_POST)
        img = post.preview_images[0]
        assert isinstance(img, RedditPreviewImage)
        assert img.url == "https://preview.redd.it/img.jpg"

    def test_reddit_post_awards_parsed(self) -> None:
        post = RedditPost.model_validate(SAMPLE_POST)
        award = post.awards[0]
        assert isinstance(award, RedditAward)
        assert award.count == 1

    # -- RedditComment --

    def test_reddit_comment_full(self) -> None:
        comment = RedditComment.model_validate(SAMPLE_COMMENT)
        assert comment.id == "cmt001"
        assert comment.fullname == "t1_cmt001"
        assert comment.author == "commenter1"
        assert comment.author_fullname == "t2_commenter1"
        assert comment.author_flair_type == "text"
        assert comment.body == "Great post!"
        assert comment.body_html == "<p>Great post!</p>"
        assert comment.subreddit == "python"
        assert comment.subreddit_id == "t5_2qh0y"
        assert comment.subreddit_name_prefixed == "r/python"
        assert comment.subreddit_type == "public"
        assert comment.score == 42
        assert comment.ups == 45
        assert comment.downs == 3
        assert comment.depth == 0
        assert comment.parent_id == "t3_abc123"
        assert comment.created_at == "2023-11-14T22:30:00+00:00"
        assert comment.send_replies is True
        assert comment.is_score_hidden is False
        assert comment.replies == []

    def test_reddit_comment_minimal(self) -> None:
        comment = RedditComment(id="c1")
        assert comment.score == 0
        assert comment.is_submitter is False
        assert comment.distinguished is None
        assert comment.depth == 0
        assert comment.fullname == ""
        assert comment.body == ""
        assert comment.author_flair_type is None
        assert comment.subreddit_id is None
        assert comment.subreddit_name_prefixed is None
        assert comment.subreddit_type is None
        assert comment.created_at is None
        assert comment.edited_at is None
        assert comment.send_replies is False

    def test_reddit_comment_is_frozen(self) -> None:
        comment = RedditComment.model_validate(SAMPLE_COMMENT)
        with pytest.raises(Exception):  # noqa: B017
            comment.body = "mutated"  # type: ignore[misc]

    def test_reddit_comment_nested_replies(self) -> None:
        nested: dict[str, Any] = {
            **SAMPLE_COMMENT,
            "id": "cmt002",
            "replies": [SAMPLE_COMMENT],
        }
        comment = RedditComment.model_validate(nested)
        assert len(comment.replies) == 1
        assert comment.replies[0].id == "cmt001"

    # -- RedditSubreddit --

    def test_reddit_subreddit_full(self) -> None:
        sub = RedditSubreddit.model_validate(SAMPLE_SUBREDDIT)
        assert sub.id == "2qh0y"
        assert sub.fullname == "t5_2qh0y"
        assert sub.name == "python"
        assert sub.display_name_prefixed == "r/python"
        assert sub.public_description == "Python news"
        assert sub.public_description_html == "<p>Python news</p>"
        assert sub.submit_text == "Submit a post"
        assert sub.submit_text_html == "<p>Submit a post</p>"
        assert sub.header_title == "Python"
        assert sub.subscribers == 1500000
        assert sub.active_users == 3200
        assert sub.created_at == "2008-01-11T00:00:00+00:00"
        assert sub.is_nsfw is False
        assert sub.is_advertiser_friendly is True
        assert sub.advertiser_category == "Technology"
        assert sub.header_url is None
        assert sub.banner_background_color == "#ffffff"
        assert sub.allow_discovery is True
        assert sub.spoilers_enabled is True
        assert sub.emojis_enabled is False
        assert sub.free_form_reports is True
        assert sub.accept_followers is True
        assert sub.restrict_posting is False
        assert sub.link_flair_enabled is True
        assert sub.link_flair_position == "left"
        assert sub.user_flair_enabled is True
        assert sub.user_flair_position == "right"
        assert sub.comment_score_hide_mins == 60
        assert sub.should_archive_posts is True
        assert sub.allowed_media_in_comments == ["gif", "image"]

    def test_reddit_subreddit_minimal(self) -> None:
        sub = RedditSubreddit(id="s1", name="test")
        assert sub.subscribers == 0
        assert sub.is_nsfw is False
        assert sub.icon_url is None
        assert sub.fullname == ""
        assert sub.display_name_prefixed is None
        assert sub.public_description_html is None
        assert sub.submit_text == ""
        assert sub.submit_text_html is None
        assert sub.header_title is None
        assert sub.is_advertiser_friendly is True
        assert sub.advertiser_category is None
        assert sub.created_at is None
        assert sub.header_url is None
        assert sub.banner_background_color is None
        assert sub.allow_discovery is True
        assert sub.spoilers_enabled is False
        assert sub.emojis_enabled is False
        assert sub.free_form_reports is True
        assert sub.accept_followers is True
        assert sub.restrict_posting is False
        assert sub.link_flair_enabled is False
        assert sub.link_flair_position is None
        assert sub.user_flair_enabled is False
        assert sub.user_flair_position is None
        assert sub.comment_score_hide_mins == 0
        assert sub.should_archive_posts is False
        assert sub.allowed_media_in_comments == []

    def test_reddit_subreddit_is_frozen(self) -> None:
        sub = RedditSubreddit.model_validate(SAMPLE_SUBREDDIT)
        with pytest.raises(Exception):  # noqa: B017
            sub.name = "mutated"  # type: ignore[misc]

    # -- RedditUser --

    def test_reddit_user_full(self) -> None:
        user = RedditUser.model_validate(SAMPLE_USER)
        assert user.id == "usr001"
        assert user.fullname == "t2_usr001"
        assert user.name == "redditor42"
        assert user.display_name_prefixed == "u/redditor42"
        assert user.icon_url == "https://www.redditstatic.com/avatars/avatar.png"
        assert user.snoovatar_url == "https://www.redditstatic.com/snoovatar/avatar.png"
        assert user.banner_url is None
        assert user.profile_title == "All about Python"
        assert user.profile_url == "/user/redditor42/"
        assert user.link_karma == 5000
        assert user.comment_karma == 12000
        assert user.awardee_karma == 100
        assert user.awarder_karma == 50
        assert user.total_karma == 17150
        assert user.created_at == "2014-05-13T16:53:20+00:00"
        assert user.has_verified_email is True
        assert user.verified is True
        assert user.accepts_followers is True
        assert user.has_subscribed is False
        assert user.is_mod is True
        assert user.is_gold is False
        assert user.is_suspended is False
        assert user.pref_show_snoovatar is True

    def test_reddit_user_minimal(self) -> None:
        user = RedditUser(id="u1", name="user")
        assert user.link_karma == 0
        assert user.comment_karma == 0
        assert user.is_gold is False
        assert user.is_mod is False
        assert user.fullname is None
        assert user.display_name_prefixed is None
        assert user.snoovatar_url is None
        assert user.banner_url is None
        assert user.profile_title is None
        assert user.profile_url is None
        assert user.created_at is None
        assert user.verified is False
        assert user.accepts_followers is False
        assert user.has_subscribed is False
        assert user.pref_show_snoovatar is False

    def test_reddit_user_is_frozen(self) -> None:
        user = RedditUser.model_validate(SAMPLE_USER)
        with pytest.raises(Exception):  # noqa: B017
            user.name = "mutated"  # type: ignore[misc]

    # -- RedditRule --

    def test_reddit_rule(self) -> None:
        rule = RedditRule.model_validate(SAMPLE_RULE)
        assert rule.short_name == "Be nice"
        assert rule.description == "Treat others with respect"
        assert rule.description_html == "<p>Treat others with respect</p>"
        assert rule.kind == "all"
        assert rule.priority == 1
        assert rule.violation_reason == "Being mean"

    def test_reddit_rule_minimal(self) -> None:
        rule = RedditRule(short_name="Rule 1")
        assert rule.description == ""
        assert rule.description_html is None
        assert rule.kind == "all"
        assert rule.priority == 0
        assert rule.violation_reason is None

    def test_reddit_rule_is_frozen(self) -> None:
        rule = RedditRule.model_validate(SAMPLE_RULE)
        with pytest.raises(Exception):  # noqa: B017
            rule.short_name = "mutated"  # type: ignore[misc]

    # -- RedditWikiPage --

    def test_reddit_wiki_page(self) -> None:
        page = RedditWikiPage.model_validate(SAMPLE_WIKI_PAGE)
        assert page.title == "rules"
        assert page.content_md == "# Rules\n\n- Be nice"
        assert page.revision_by == "moderator1"
        assert page.revision_date == 1700000000.0

    def test_reddit_wiki_page_minimal(self) -> None:
        page = RedditWikiPage(title="index")
        assert page.content_md == ""
        assert page.content_html is None
        assert page.revision_by is None

    def test_reddit_wiki_page_is_frozen(self) -> None:
        page = RedditWikiPage.model_validate(SAMPLE_WIKI_PAGE)
        with pytest.raises(Exception):  # noqa: B017
            page.title = "mutated"  # type: ignore[misc]

    # -- RedditTrophy --

    def test_reddit_trophy(self) -> None:
        trophy = RedditTrophy.model_validate(SAMPLE_TROPHY)
        assert trophy.name == "Verified Email"
        assert trophy.icon_url == "https://www.redditstatic.com/awards/trophies/email.png"
        assert trophy.url is None

    def test_reddit_trophy_minimal(self) -> None:
        trophy = RedditTrophy(name="Some Trophy")
        assert trophy.description is None
        assert trophy.icon_url is None
        assert trophy.url is None

    def test_reddit_trophy_is_frozen(self) -> None:
        trophy = RedditTrophy.model_validate(SAMPLE_TROPHY)
        with pytest.raises(Exception):  # noqa: B017
            trophy.name = "mutated"  # type: ignore[misc]

    # -- Response envelopes --

    def test_search_posts_response(self) -> None:
        resp = SearchPostsResponse.model_validate(SEARCH_POSTS_RESPONSE)
        assert len(resp.posts) == 1
        assert resp.posts[0].id == "abc123"
        assert resp.after == "t3_xyz789"
        assert resp.count == 1

    def test_search_posts_response_empty(self) -> None:
        resp = SearchPostsResponse.model_validate({"posts": [], "count": 0})
        assert resp.posts == []
        assert resp.after is None

    def test_subreddit_posts_response(self) -> None:
        resp = SubredditPostsResponse.model_validate(SUBREDDIT_POSTS_RESPONSE)
        assert len(resp.posts) == 1
        assert resp.subreddit == "python"

    def test_post_detail_response(self) -> None:
        resp = PostDetailResponse.model_validate(POST_DETAIL_RESPONSE)
        assert resp.post is not None
        assert resp.post.id == "abc123"

    def test_post_detail_response_null_post(self) -> None:
        resp = PostDetailResponse.model_validate({"post": None})
        assert resp.post is None

    def test_post_comments_response(self) -> None:
        resp = PostCommentsResponse.model_validate(POST_COMMENTS_RESPONSE)
        assert len(resp.comments) == 1
        assert resp.comments[0].id == "cmt001"
        assert resp.post is not None

    def test_post_duplicates_response(self) -> None:
        resp = PostDuplicatesResponse.model_validate(POST_DUPLICATES_RESPONSE)
        assert len(resp.posts) == 1

    def test_trending_posts_response(self) -> None:
        resp = TrendingPostsResponse.model_validate(TRENDING_POSTS_RESPONSE)
        assert len(resp.posts) == 1

    def test_user_profile_response(self) -> None:
        resp = UserProfileResponse.model_validate(USER_PROFILE_RESPONSE)
        assert resp.user is not None
        assert resp.user.name == "redditor42"

    def test_user_posts_response(self) -> None:
        resp = UserPostsResponse.model_validate(USER_POSTS_RESPONSE)
        assert len(resp.posts) == 1

    def test_user_comments_response(self) -> None:
        resp = UserCommentsResponse.model_validate(USER_COMMENTS_RESPONSE)
        assert len(resp.comments) == 1
        assert resp.comments[0].id == "cmt001"

    def test_user_moderated_response(self) -> None:
        resp = UserModeratedResponse.model_validate(USER_MODERATED_RESPONSE)
        assert len(resp.subreddits) == 1
        assert resp.subreddits[0].name == "python"

    def test_user_trophies_response(self) -> None:
        resp = UserTrophiesResponse.model_validate(USER_TROPHIES_RESPONSE)
        assert len(resp.trophies) == 1
        assert resp.trophies[0].name == "Verified Email"

    def test_subreddits_list_response(self) -> None:
        resp = SubredditsListResponse.model_validate(SUBREDDITS_LIST_RESPONSE)
        assert len(resp.subreddits) == 1

    def test_subreddit_rules_response(self) -> None:
        resp = SubredditRulesResponse.model_validate(SUBREDDIT_RULES_RESPONSE)
        assert len(resp.rules) == 1
        assert resp.subreddit == "python"

    def test_subreddit_wiki_pages_response(self) -> None:
        resp = SubredditWikiPagesResponse.model_validate(SUBREDDIT_WIKI_PAGES_RESPONSE)
        assert resp.pages == ["rules", "faq"]
        assert resp.subreddit == "python"

    def test_subreddit_wiki_page_response(self) -> None:
        resp = SubredditWikiPageResponse.model_validate(SUBREDDIT_WIKI_PAGE_RESPONSE)
        assert resp.page is not None
        assert resp.page.title == "rules"
        assert resp.subreddit == "python"


# ===========================================================================
# TestRedditClient
# ===========================================================================


class TestRedditClient:
    """Tests for RedditClient sub-client wiring."""

    def test_search_property(self, reddit_client: RedditClient) -> None:
        assert isinstance(reddit_client.search, SearchClient)

    def test_posts_property(self, reddit_client: RedditClient) -> None:
        assert isinstance(reddit_client.posts, PostsClient)

    def test_subreddits_property(self, reddit_client: RedditClient) -> None:
        assert isinstance(reddit_client.subreddits, SubredditsClient)

    def test_users_property(self, reddit_client: RedditClient) -> None:
        assert isinstance(reddit_client.users, UsersClient)

    def test_sub_clients_are_stable(self, reddit_client: RedditClient) -> None:
        """Sub-client properties return the same instance on repeated access."""
        assert reddit_client.search is reddit_client.search
        assert reddit_client.posts is reddit_client.posts
        assert reddit_client.subreddits is reddit_client.subreddits
        assert reddit_client.users is reddit_client.users


# ===========================================================================
# TestSearchClient
# ===========================================================================


class TestSearchClient:
    """Tests for SearchClient methods."""

    async def test_posts_default_params(
        self, search_client: SearchClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = SEARCH_POSTS_RESPONSE
        result = await search_client.posts("python asyncio")

        assert isinstance(result, SearchPostsResponse)
        assert len(result.posts) == 1

        call_args = mock_base_client.get.call_args
        assert call_args[0][0] == "/v1/reddit/search/posts"
        params = call_args[1]["params"]
        assert params["query"] == "python asyncio"
        assert params["sort"] == "relevance"
        assert params["time_filter"] == "all"
        assert params["limit"] == 25

    async def test_posts_with_filters(
        self, search_client: SearchClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = SEARCH_POSTS_RESPONSE
        await search_client.posts(
            "python",
            subreddit="learnpython",
            sort="new",
            time_filter="week",
            limit=50,
            after="t3_abc",
        )

        params = mock_base_client.get.call_args[1]["params"]
        assert params["subreddit"] == "learnpython"
        assert params["sort"] == "new"
        assert params["time_filter"] == "week"
        assert params["limit"] == 50
        assert params["after"] == "t3_abc"

    async def test_subreddits_default_params(
        self, search_client: SearchClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = SUBREDDITS_LIST_RESPONSE
        result = await search_client.subreddits("programming")

        assert isinstance(result, SubredditsListResponse)
        call_args = mock_base_client.get.call_args
        assert call_args[0][0] == "/v1/reddit/search/subreddits"
        params = call_args[1]["params"]
        assert params["query"] == "programming"
        assert params["limit"] == 25

    async def test_users_default_params(
        self, search_client: SearchClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = {
            "users": [SAMPLE_USER],
            "after": None,
            "count": 1,
        }
        await search_client.users("redditor")

        call_args = mock_base_client.get.call_args
        assert call_args[0][0] == "/v1/reddit/search/users"
        assert call_args[1]["params"]["query"] == "redditor"

    async def test_domain_posts_default_params(
        self, search_client: SearchClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = SEARCH_POSTS_RESPONSE
        result = await search_client.domain_posts("github.com")

        assert isinstance(result, SearchPostsResponse)
        call_args = mock_base_client.get.call_args
        assert call_args[0][0] == "/v1/reddit/search/domain"
        params = call_args[1]["params"]
        assert params["domain"] == "github.com"
        assert params["sort"] == "relevance"

    async def test_posts_returns_search_posts_response(
        self, search_client: SearchClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = SEARCH_POSTS_RESPONSE
        result = await search_client.posts("test")
        assert isinstance(result, SearchPostsResponse)


# ===========================================================================
# TestPostsClient
# ===========================================================================


class TestPostsClient:
    """Tests for PostsClient methods."""

    async def test_trending_default_params(
        self, posts_client: PostsClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = TRENDING_POSTS_RESPONSE
        result = await posts_client.trending()

        assert isinstance(result, TrendingPostsResponse)
        call_args = mock_base_client.get.call_args
        assert call_args[0][0] == "/v1/reddit/posts/trending"
        params = call_args[1]["params"]
        assert params["limit"] == 25

    async def test_trending_with_params(
        self, posts_client: PostsClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = TRENDING_POSTS_RESPONSE
        await posts_client.trending(limit=10, after="t3_abc")

        params = mock_base_client.get.call_args[1]["params"]
        assert params["limit"] == 10
        assert params["after"] == "t3_abc"

    async def test_get(self, posts_client: PostsClient, mock_base_client: MagicMock) -> None:
        mock_base_client.get.return_value = POST_DETAIL_RESPONSE
        result = await posts_client.get("abc123")

        assert isinstance(result, PostDetailResponse)
        assert result.post is not None
        assert result.post.id == "abc123"

        call_args = mock_base_client.get.call_args
        assert call_args[0][0] == "/v1/reddit/posts/abc123"

    async def test_comments_default_params(
        self, posts_client: PostsClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = POST_COMMENTS_RESPONSE
        result = await posts_client.comments("abc123")

        assert isinstance(result, PostCommentsResponse)
        assert len(result.comments) == 1

        call_args = mock_base_client.get.call_args
        assert call_args[0][0] == "/v1/reddit/posts/abc123/comments"
        params = call_args[1]["params"]
        assert params["sort"] == "best"
        assert params["limit"] == 25

    async def test_comments_with_params(
        self, posts_client: PostsClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = POST_COMMENTS_RESPONSE
        await posts_client.comments("abc123", sort="top", limit=100, depth=3)

        params = mock_base_client.get.call_args[1]["params"]
        assert params["sort"] == "top"
        assert params["limit"] == 100
        assert params["depth"] == 3

    async def test_duplicates(self, posts_client: PostsClient, mock_base_client: MagicMock) -> None:
        mock_base_client.get.return_value = POST_DUPLICATES_RESPONSE
        result = await posts_client.duplicates("abc123")

        assert isinstance(result, PostDuplicatesResponse)
        call_args = mock_base_client.get.call_args
        assert call_args[0][0] == "/v1/reddit/posts/abc123/duplicates"


# ===========================================================================
# TestSubredditsClient
# ===========================================================================


class TestSubredditsClient:
    """Tests for SubredditsClient methods."""

    async def test_get(
        self, subreddits_client: SubredditsClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = {"subreddit": SAMPLE_SUBREDDIT}
        await subreddits_client.get("python")

        call_args = mock_base_client.get.call_args
        assert call_args[0][0] == "/v1/reddit/subreddits/python"

    async def test_posts_default_params(
        self, subreddits_client: SubredditsClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = SUBREDDIT_POSTS_RESPONSE
        result = await subreddits_client.posts("python")

        assert isinstance(result, SubredditPostsResponse)
        call_args = mock_base_client.get.call_args
        assert call_args[0][0] == "/v1/reddit/subreddits/python/posts"
        params = call_args[1]["params"]
        assert params["sort"] == "hot"
        assert params["limit"] == 25

    async def test_posts_with_params(
        self, subreddits_client: SubredditsClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = SUBREDDIT_POSTS_RESPONSE
        await subreddits_client.posts(
            "python", sort="top", time_filter="month", limit=50, after="t3_abc"
        )

        params = mock_base_client.get.call_args[1]["params"]
        assert params["sort"] == "top"
        assert params["time_filter"] == "month"
        assert params["limit"] == 50
        assert params["after"] == "t3_abc"

    async def test_rules(
        self, subreddits_client: SubredditsClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = SUBREDDIT_RULES_RESPONSE
        result = await subreddits_client.rules("python")

        assert isinstance(result, SubredditRulesResponse)
        assert len(result.rules) == 1
        call_args = mock_base_client.get.call_args
        assert call_args[0][0] == "/v1/reddit/subreddits/python/rules"

    async def test_wiki_pages(
        self, subreddits_client: SubredditsClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = SUBREDDIT_WIKI_PAGES_RESPONSE
        result = await subreddits_client.wiki_pages("python")

        assert isinstance(result, SubredditWikiPagesResponse)
        assert result.pages == ["rules", "faq"]
        call_args = mock_base_client.get.call_args
        assert call_args[0][0] == "/v1/reddit/subreddits/python/wiki"

    async def test_wiki_page(
        self, subreddits_client: SubredditsClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = SUBREDDIT_WIKI_PAGE_RESPONSE
        result = await subreddits_client.wiki_page("python", "rules")

        assert isinstance(result, SubredditWikiPageResponse)
        assert result.page is not None
        assert result.page.title == "rules"
        call_args = mock_base_client.get.call_args
        assert call_args[0][0] == "/v1/reddit/subreddits/python/wiki/rules"

    async def test_popular_default_params(
        self, subreddits_client: SubredditsClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = SUBREDDITS_LIST_RESPONSE
        result = await subreddits_client.popular()

        assert isinstance(result, SubredditsListResponse)
        call_args = mock_base_client.get.call_args
        assert call_args[0][0] == "/v1/reddit/subreddits/popular"
        params = call_args[1]["params"]
        assert params["limit"] == 25

    async def test_new_default_params(
        self, subreddits_client: SubredditsClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = SUBREDDITS_LIST_RESPONSE
        result = await subreddits_client.new()

        assert isinstance(result, SubredditsListResponse)
        call_args = mock_base_client.get.call_args
        assert call_args[0][0] == "/v1/reddit/subreddits/new"


# ===========================================================================
# TestUsersClient
# ===========================================================================


class TestUsersClient:
    """Tests for UsersClient methods."""

    async def test_get(self, users_client: UsersClient, mock_base_client: MagicMock) -> None:
        mock_base_client.get.return_value = USER_PROFILE_RESPONSE
        result = await users_client.get("redditor42")

        assert isinstance(result, UserProfileResponse)
        assert result.user is not None
        assert result.user.name == "redditor42"

        call_args = mock_base_client.get.call_args
        assert call_args[0][0] == "/v1/reddit/users/redditor42"

    async def test_posts_default_params(
        self, users_client: UsersClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = USER_POSTS_RESPONSE
        result = await users_client.posts("redditor42")

        assert isinstance(result, UserPostsResponse)
        call_args = mock_base_client.get.call_args
        assert call_args[0][0] == "/v1/reddit/users/redditor42/posts"
        params = call_args[1]["params"]
        assert params["sort"] == "new"
        assert params["limit"] == 25

    async def test_posts_with_params(
        self, users_client: UsersClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = USER_POSTS_RESPONSE
        await users_client.posts("redditor42", sort="top", time_filter="year", limit=10)

        params = mock_base_client.get.call_args[1]["params"]
        assert params["sort"] == "top"
        assert params["time_filter"] == "year"
        assert params["limit"] == 10

    async def test_comments_default_params(
        self, users_client: UsersClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = USER_COMMENTS_RESPONSE
        result = await users_client.comments("redditor42")

        assert isinstance(result, UserCommentsResponse)
        call_args = mock_base_client.get.call_args
        assert call_args[0][0] == "/v1/reddit/users/redditor42/comments"
        params = call_args[1]["params"]
        assert params["sort"] == "new"
        assert params["limit"] == 25

    async def test_moderated(self, users_client: UsersClient, mock_base_client: MagicMock) -> None:
        mock_base_client.get.return_value = USER_MODERATED_RESPONSE
        result = await users_client.moderated("redditor42")

        assert isinstance(result, UserModeratedResponse)
        call_args = mock_base_client.get.call_args
        assert call_args[0][0] == "/v1/reddit/users/redditor42/moderated"

    async def test_trophies(self, users_client: UsersClient, mock_base_client: MagicMock) -> None:
        mock_base_client.get.return_value = USER_TROPHIES_RESPONSE
        result = await users_client.trophies("redditor42")

        assert isinstance(result, UserTrophiesResponse)
        assert len(result.trophies) == 1
        call_args = mock_base_client.get.call_args
        assert call_args[0][0] == "/v1/reddit/users/redditor42/trophies"


# ===========================================================================
# TestScrapeBadgerRedditProperty
# ===========================================================================


class TestScrapeBadgerRedditProperty:
    """Tests for reddit property on main ScrapeBadger client."""

    def test_reddit_property_returns_reddit_client(self) -> None:
        from scrapebadger import ScrapeBadger

        client = ScrapeBadger(api_key="test-key")
        assert isinstance(client.reddit, RedditClient)

    def test_reddit_property_is_stable(self) -> None:
        from scrapebadger import ScrapeBadger

        client = ScrapeBadger(api_key="test-key")
        assert client.reddit is client.reddit


# ===========================================================================
# TestRedditImports
# ===========================================================================


class TestRedditImports:
    """Tests that Reddit types are importable from the reddit package."""

    def test_reddit_client_importable(self) -> None:
        from scrapebadger.reddit import RedditClient as _  # noqa: F401

    def test_reddit_post_importable(self) -> None:
        from scrapebadger.reddit import RedditPost as _  # noqa: F401

    def test_reddit_comment_importable(self) -> None:
        from scrapebadger.reddit import RedditComment as _  # noqa: F401

    def test_reddit_subreddit_importable(self) -> None:
        from scrapebadger.reddit import RedditSubreddit as _  # noqa: F401

    def test_reddit_user_importable(self) -> None:
        from scrapebadger.reddit import RedditUser as _  # noqa: F401

    def test_reddit_rule_importable(self) -> None:
        from scrapebadger.reddit import RedditRule as _  # noqa: F401

    def test_reddit_wiki_page_importable(self) -> None:
        from scrapebadger.reddit import RedditWikiPage as _  # noqa: F401

    def test_reddit_trophy_importable(self) -> None:
        from scrapebadger.reddit import RedditTrophy as _  # noqa: F401

    def test_reddit_preview_image_importable(self) -> None:
        from scrapebadger.reddit import RedditPreviewImage as _  # noqa: F401

    def test_reddit_media_importable(self) -> None:
        from scrapebadger.reddit import RedditMedia as _  # noqa: F401

    def test_reddit_award_importable(self) -> None:
        from scrapebadger.reddit import RedditAward as _  # noqa: F401

    def test_reddit_user_summary_importable(self) -> None:
        from scrapebadger.reddit import RedditUserSummary as _  # noqa: F401

    def test_search_posts_response_importable(self) -> None:
        from scrapebadger.reddit import SearchPostsResponse as _  # noqa: F401

    def test_subreddit_posts_response_importable(self) -> None:
        from scrapebadger.reddit import SubredditPostsResponse as _  # noqa: F401

    def test_post_detail_response_importable(self) -> None:
        from scrapebadger.reddit import PostDetailResponse as _  # noqa: F401

    def test_post_comments_response_importable(self) -> None:
        from scrapebadger.reddit import PostCommentsResponse as _  # noqa: F401

    def test_user_profile_response_importable(self) -> None:
        from scrapebadger.reddit import UserProfileResponse as _  # noqa: F401

    def test_top_level_reddit_post_importable(self) -> None:
        from scrapebadger import RedditPost as _  # noqa: F401

    def test_top_level_reddit_user_importable(self) -> None:
        from scrapebadger import RedditUser as _  # noqa: F401
