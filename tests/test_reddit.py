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
    RedditComment,
    RedditPost,
    RedditRule,
    RedditSubreddit,
    RedditTrophy,
    RedditUser,
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
# Shared sample data — field names match the canonical backend model exactly.
# Only fields available via old.reddit.com HTML/RSS are present (0.9.0+).
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
    "subreddit": "python",
    "subreddit_id": "t5_2qh0y",
    "subreddit_name_prefixed": "r/python",
    "subreddit_type": "public",
    "score": 1234,
    "num_comments": 56,
    "num_crossposts": 3,
    "created_utc": 1700000000.0,
    "created_at": "2023-11-14T22:13:20+00:00",
    "is_self": True,
    "is_gallery": False,
    "is_nsfw": False,
    "is_spoiler": False,
    "is_stickied": False,
    "is_original_content": True,
    "link_flair_text": "Discussion",
    "gilded": 0,
}

SAMPLE_COMMENT: dict[str, Any] = {
    "id": "cmt001",
    "fullname": "t1_cmt001",
    "body": "Great post!",
    "body_html": "<p>Great post!</p>",
    "author": "commenter1",
    "author_fullname": "t2_commenter1",
    "subreddit": "python",
    "subreddit_id": "t5_2qh0y",
    "subreddit_name_prefixed": "r/python",
    "post_id": "abc123",
    "permalink": "/r/python/comments/abc123/hello_reddit/cmt001/",
    "score": 42,
    "depth": 0,
    "created_utc": 1700001000.0,
    "created_at": "2023-11-14T22:30:00+00:00",
    "is_stickied": False,
    "replies": [],
}

SAMPLE_SUBREDDIT: dict[str, Any] = {
    "id": "2qh0y",
    "fullname": "t5_2qh0y",
    "name": "python",
    "display_name_prefixed": "r/python",
    "title": "Python - The programming language",
    "description": "News about the dynamic, interpreted programming language Python",
    "public_description": "Python news",
    "url": "/r/python/",
    "created_utc": 1200000000.0,
    "created_at": "2008-01-11T00:00:00+00:00",
    "is_nsfw": False,
}

SAMPLE_USER: dict[str, Any] = {
    "name": "redditor42",
    "display_name_prefixed": "u/redditor42",
    "link_karma": 5000,
    "comment_karma": 12000,
    "total_karma": 17000,
    "created_utc": 1400000000.0,
    "created_at": "2014-05-13T16:53:20+00:00",
    "is_gold": False,
}

SAMPLE_RULE: dict[str, Any] = {
    "priority": 1,
    "short_name": "Be nice",
    "description": "Treat others with respect",
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

    # -- RedditPost --

    def test_reddit_post_full(self) -> None:
        post = RedditPost.model_validate(SAMPLE_POST)
        assert post.id == "abc123"
        assert post.fullname == "t3_abc123"
        assert post.title == "Hello Reddit"
        assert post.selftext == "This is the post body"
        assert post.selftext_html == "<p>This is the post body</p>"
        assert post.url == "https://www.reddit.com/r/python/comments/abc123/hello_reddit/"
        assert post.permalink == "/r/python/comments/abc123/hello_reddit/"
        assert post.domain == "self.python"
        assert post.author == "user42"
        assert post.author_fullname == "t2_user42"
        assert post.subreddit == "python"
        assert post.subreddit_id == "t5_2qh0y"
        assert post.subreddit_name_prefixed == "r/python"
        assert post.subreddit_type == "public"
        assert post.score == 1234
        assert post.num_comments == 56
        assert post.num_crossposts == 3
        assert post.created_utc == 1700000000.0
        assert post.created_at == "2023-11-14T22:13:20+00:00"
        assert post.is_self is True
        assert post.is_gallery is False
        assert post.is_nsfw is False
        assert post.is_spoiler is False
        assert post.is_stickied is False
        assert post.is_original_content is True
        assert post.link_flair_text == "Discussion"
        assert post.gilded == 0

    def test_reddit_post_minimal(self) -> None:
        post = RedditPost(id="x1", title="Test")
        assert post.score == 0
        assert post.num_comments == 0
        assert post.selftext == ""
        assert post.link_flair_text is None
        assert post.fullname == ""
        assert post.num_crossposts == 0
        assert post.created_at is None
        assert post.is_self is False
        assert post.is_gallery is False
        assert post.is_nsfw is False
        assert post.is_spoiler is False
        assert post.is_stickied is False
        assert post.is_original_content is False
        assert post.gilded == 0

    def test_reddit_post_is_frozen(self) -> None:
        post = RedditPost.model_validate(SAMPLE_POST)
        with pytest.raises(Exception):  # noqa: B017
            post.title = "mutated"  # type: ignore[misc]

    def test_reddit_post_extra_fields_ignored(self) -> None:
        data = {**SAMPLE_POST, "unknown_future_field": "value"}
        post = RedditPost.model_validate(data)
        assert post.id == "abc123"

    def test_reddit_post_removed_fields_absent(self) -> None:
        """Fields removed in 0.9.0 must not be present on the model."""
        post = RedditPost.model_validate(SAMPLE_POST)
        for attr in (
            "ups",
            "downs",
            "upvote_ratio",
            "view_count",
            "num_duplicates",
            "edited",
            "edited_at",
            "is_video",
            "is_locked",
            "is_archived",
            "is_pinned",
            "is_robot_indexable",
            "is_meta",
            "is_crosspostable",
            "send_replies",
            "link_flair_background_color",
            "link_flair_text_color",
            "link_flair_template_id",
            "link_flair_type",
            "link_flair_css_class",
            "distinguished",
            "thumbnail",
            "thumbnail_width",
            "thumbnail_height",
            "post_hint",
            "preview_images",
            "media",
            "gallery_data",
            "crosspost_parent",
            "suggested_sort",
            "total_awards",
            "awards",
            "content_categories",
            "removed_by_category",
            "treatment_tags",
            "subreddit_subscribers",
            "author_flair_text",
            "author_flair_type",
            "author_flair_template_id",
        ):
            assert not hasattr(post, attr), f"RedditPost should not have field: {attr}"

    # -- RedditComment --

    def test_reddit_comment_full(self) -> None:
        comment = RedditComment.model_validate(SAMPLE_COMMENT)
        assert comment.id == "cmt001"
        assert comment.fullname == "t1_cmt001"
        assert comment.author == "commenter1"
        assert comment.author_fullname == "t2_commenter1"
        assert comment.body == "Great post!"
        assert comment.body_html == "<p>Great post!</p>"
        assert comment.subreddit == "python"
        assert comment.subreddit_id == "t5_2qh0y"
        assert comment.subreddit_name_prefixed == "r/python"
        assert comment.post_id == "abc123"
        assert comment.permalink == "/r/python/comments/abc123/hello_reddit/cmt001/"
        assert comment.score == 42
        assert comment.depth == 0
        assert comment.created_utc == 1700001000.0
        assert comment.created_at == "2023-11-14T22:30:00+00:00"
        assert comment.is_stickied is False
        assert comment.replies == []

    def test_reddit_comment_minimal(self) -> None:
        comment = RedditComment(id="c1")
        assert comment.score == 0
        assert comment.depth == 0
        assert comment.fullname == ""
        assert comment.body == ""
        assert comment.author_fullname is None
        assert comment.subreddit_id is None
        assert comment.subreddit_name_prefixed is None
        assert comment.post_id is None
        assert comment.created_at is None
        assert comment.is_stickied is False
        assert comment.replies == []

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

    def test_reddit_comment_removed_fields_absent(self) -> None:
        """Fields removed in 0.9.0 must not be present on the model."""
        comment = RedditComment.model_validate(SAMPLE_COMMENT)
        for attr in (
            "ups",
            "downs",
            "controversiality",
            "edited",
            "edited_at",
            "gilded",
            "is_locked",
            "is_score_hidden",
            "is_submitter",
            "parent_id",
            "post_title",
            "send_replies",
            "subreddit_type",
            "total_awards",
            "distinguished",
            "author_flair_text",
            "author_flair_type",
        ):
            assert not hasattr(comment, attr), f"RedditComment should not have field: {attr}"

    # -- RedditSubreddit --

    def test_reddit_subreddit_full(self) -> None:
        sub = RedditSubreddit.model_validate(SAMPLE_SUBREDDIT)
        assert sub.id == "2qh0y"
        assert sub.fullname == "t5_2qh0y"
        assert sub.name == "python"
        assert sub.display_name_prefixed == "r/python"
        assert sub.title == "Python - The programming language"
        assert sub.description == "News about the dynamic, interpreted programming language Python"
        assert sub.public_description == "Python news"
        assert sub.url == "/r/python/"
        assert sub.created_utc == 1200000000.0
        assert sub.created_at == "2008-01-11T00:00:00+00:00"
        assert sub.is_nsfw is False

    def test_reddit_subreddit_minimal(self) -> None:
        sub = RedditSubreddit(id="s1", name="test")
        assert sub.is_nsfw is False
        assert sub.fullname == ""
        assert sub.display_name_prefixed is None
        assert sub.public_description == ""
        assert sub.description == ""
        assert sub.created_at is None

    def test_reddit_subreddit_is_frozen(self) -> None:
        sub = RedditSubreddit.model_validate(SAMPLE_SUBREDDIT)
        with pytest.raises(Exception):  # noqa: B017
            sub.name = "mutated"  # type: ignore[misc]

    def test_reddit_subreddit_removed_fields_absent(self) -> None:
        """Fields removed in 0.9.0 must not be present on the model."""
        sub = RedditSubreddit.model_validate(SAMPLE_SUBREDDIT)
        for attr in (
            "subscribers",
            "active_users",
            "description_html",
            "public_description_html",
            "submit_text",
            "submit_text_html",
            "header_title",
            "type",
            "submission_type",
            "is_quarantined",
            "is_advertiser_friendly",
            "advertiser_category",
            "language",
            "icon_url",
            "header_url",
            "banner_url",
            "banner_background_color",
            "primary_color",
            "key_color",
            "wiki_enabled",
            "allow_images",
            "allow_videos",
            "allow_galleries",
            "allow_polls",
            "allow_discovery",
            "spoilers_enabled",
            "emojis_enabled",
            "free_form_reports",
            "accept_followers",
            "restrict_posting",
            "link_flair_enabled",
            "link_flair_position",
            "user_flair_enabled",
            "user_flair_position",
            "comment_score_hide_mins",
            "should_archive_posts",
            "allowed_media_in_comments",
        ):
            assert not hasattr(sub, attr), f"RedditSubreddit should not have field: {attr}"

    # -- RedditUser --

    def test_reddit_user_full(self) -> None:
        user = RedditUser.model_validate(SAMPLE_USER)
        assert user.name == "redditor42"
        assert user.display_name_prefixed == "u/redditor42"
        assert user.link_karma == 5000
        assert user.comment_karma == 12000
        assert user.total_karma == 17000
        assert user.created_utc == 1400000000.0
        assert user.created_at == "2014-05-13T16:53:20+00:00"
        assert user.is_gold is False

    def test_reddit_user_minimal(self) -> None:
        user = RedditUser(name="user")
        assert user.link_karma == 0
        assert user.comment_karma == 0
        assert user.total_karma == 0
        assert user.is_gold is False
        assert user.display_name_prefixed is None
        assert user.created_at is None

    def test_reddit_user_is_frozen(self) -> None:
        user = RedditUser.model_validate(SAMPLE_USER)
        with pytest.raises(Exception):  # noqa: B017
            user.name = "mutated"  # type: ignore[misc]

    def test_reddit_user_removed_fields_absent(self) -> None:
        """Fields removed in 0.9.0 must not be present on the model."""
        user = RedditUser.model_validate(SAMPLE_USER)
        for attr in (
            "id",
            "fullname",
            "description",
            "icon_url",
            "snoovatar_url",
            "banner_url",
            "profile_title",
            "profile_url",
            "awardee_karma",
            "awarder_karma",
            "has_verified_email",
            "verified",
            "accepts_followers",
            "has_subscribed",
            "is_employee",
            "is_mod",
            "is_suspended",
            "is_nsfw",
            "pref_show_snoovatar",
        ):
            assert not hasattr(user, attr), f"RedditUser should not have field: {attr}"

    # -- RedditRule --

    def test_reddit_rule(self) -> None:
        rule = RedditRule.model_validate(SAMPLE_RULE)
        assert rule.priority == 1
        assert rule.short_name == "Be nice"
        assert rule.description == "Treat others with respect"

    def test_reddit_rule_minimal(self) -> None:
        rule = RedditRule(short_name="Rule 1")
        assert rule.description == ""
        assert rule.priority == 0

    def test_reddit_rule_is_frozen(self) -> None:
        rule = RedditRule.model_validate(SAMPLE_RULE)
        with pytest.raises(Exception):  # noqa: B017
            rule.short_name = "mutated"  # type: ignore[misc]

    def test_reddit_rule_removed_fields_absent(self) -> None:
        """Fields removed in 0.9.0 must not be present on the model."""
        rule = RedditRule.model_validate(SAMPLE_RULE)
        for attr in ("description_html", "kind", "violation_reason"):
            assert not hasattr(rule, attr), f"RedditRule should not have field: {attr}"

    # -- RedditWikiPage --

    def test_reddit_wiki_page(self) -> None:
        page = RedditWikiPage.model_validate(SAMPLE_WIKI_PAGE)
        assert page.title == "rules"
        assert page.content_md == "# Rules\n\n- Be nice"
        assert page.content_html == "<h1>Rules</h1><ul><li>Be nice</li></ul>"
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
        assert trophy.description == "Verified Email"
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
        assert params["q"] == "python asyncio"
        assert params["sort"] == "relevance"
        assert params["t"] == "all"
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
        assert params["t"] == "week"
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
        assert params["q"] == "programming"
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
        assert call_args[1]["params"]["q"] == "redditor"

    async def test_domain_posts_default_params(
        self, search_client: SearchClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = SEARCH_POSTS_RESPONSE
        result = await search_client.domain_posts("github.com")

        assert isinstance(result, SearchPostsResponse)
        call_args = mock_base_client.get.call_args
        assert call_args[0][0] == "/v1/reddit/domains/github.com/posts"
        params = call_args[1]["params"]
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
        assert params["t"] == "month"
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
        assert params["t"] == "year"
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

    def test_reddit_pagination_importable(self) -> None:
        from scrapebadger.reddit import RedditPagination as _  # noqa: F401

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

    def test_removed_models_not_importable(self) -> None:
        """Helper models deleted in 0.9.0 must not be importable."""
        import importlib

        models_mod = importlib.import_module("scrapebadger.reddit.models")
        for name in ("RedditPreviewImage", "RedditMedia", "RedditAward", "RedditUserSummary"):
            assert not hasattr(models_mod, name), f"{name} should have been removed in 0.9.0"
