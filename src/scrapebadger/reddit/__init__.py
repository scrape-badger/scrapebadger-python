"""Reddit API module for ScrapeBadger SDK.

This module provides a comprehensive async client for scraping Reddit data
through the ScrapeBadger API. All methods are async and return strongly-typed
Pydantic models.

Example:
    ```python
    from scrapebadger import ScrapeBadger

    async with ScrapeBadger(api_key="your-key") as client:
        # Search for posts
        results = await client.reddit.search.posts("python asyncio")
        for post in results.posts:
            print(f"r/{post.subreddit}: {post.title} ({post.score} pts)")

        # Get subreddit posts
        hot = await client.reddit.subreddits.posts("python", sort="hot")
        print(hot.posts[0].title)

        # Get user profile
        profile = await client.reddit.users.get("spez")
        print(f"u/{profile.user.name}: {profile.user.total_karma:,} karma")
    ```
"""

from scrapebadger.reddit.client import RedditClient
from scrapebadger.reddit.models import (
    PostCommentsResponse,
    PostDetailResponse,
    PostDuplicatesResponse,
    RedditComment,
    RedditPagination,
    RedditPost,
    RedditRule,
    RedditSubreddit,
    RedditTrophy,
    RedditUser,
    RedditWikiPage,
    SearchPostsResponse,
    SearchUsersResponse,
    SubredditDetailResponse,
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

__all__ = [
    # Response envelopes — posts
    "PostCommentsResponse",
    "PostDetailResponse",
    "PostDuplicatesResponse",
    # Client
    "RedditClient",
    # Core models
    "RedditComment",
    "RedditPagination",
    "RedditPost",
    # Reference models
    "RedditRule",
    "RedditSubreddit",
    "RedditTrophy",
    "RedditUser",
    "RedditWikiPage",
    # Response envelopes — search
    "SearchPostsResponse",
    "SearchUsersResponse",
    # Response envelopes — subreddits
    "SubredditDetailResponse",
    "SubredditPostsResponse",
    "SubredditRulesResponse",
    "SubredditWikiPageResponse",
    "SubredditWikiPagesResponse",
    "SubredditsListResponse",
    # Response envelopes — trending
    "TrendingPostsResponse",
    # Response envelopes — users
    "UserCommentsResponse",
    "UserModeratedResponse",
    "UserPostsResponse",
    "UserProfileResponse",
    "UserTrophiesResponse",
]
