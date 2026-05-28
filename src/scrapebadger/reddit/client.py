"""Reddit API client combining all sub-clients.

This module provides the main RedditClient class that serves as the
entry point for all Reddit API operations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from scrapebadger.reddit.posts import PostsClient
from scrapebadger.reddit.search import SearchClient
from scrapebadger.reddit.subreddits import SubredditsClient
from scrapebadger.reddit.users import UsersClient

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class RedditClient:
    """Client for all Reddit API operations.

    This class provides access to all Reddit scraping endpoints through
    organised sub-clients for different resource types.

    Attributes:
        search: Client for searching posts, subreddits, users, and domains.
        posts: Client for fetching post details, comments, and trending posts.
        subreddits: Client for subreddit metadata, posts, rules, and wiki.
        users: Client for user profiles, posts, comments, and trophies.

    Example:
        ```python
        from scrapebadger import ScrapeBadger

        async with ScrapeBadger(api_key="your-key") as client:
            # Search for posts
            results = await client.reddit.search.posts("python asyncio")
            for post in results.posts:
                print(f"r/{post.subreddit}: {post.title}")

            # Get subreddit posts
            hot = await client.reddit.subreddits.posts("python", sort="hot")
            for post in hot.posts:
                print(f"  {post.title} — {post.score} pts")

            # Get user profile
            profile = await client.reddit.users.get("spez")
            print(f"u/{profile.user.name}: {profile.user.total_karma:,} karma")

            # Get post comments
            comments = await client.reddit.posts.comments("python", "abc123")
            for comment in comments.comments:
                print(f"  u/{comment.author}: {comment.body[:80]}")
        ```

    Note:
        This client is not instantiated directly. Instead, access it through
        the `reddit` property of the main `ScrapeBadger` client.
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize Reddit client with all sub-clients.

        Args:
            client: The base HTTP client for making API requests.
        """
        self._client = client

        # Initialize sub-clients eagerly for stable property access
        self._search = SearchClient(client)
        self._posts = PostsClient(client)
        self._subreddits = SubredditsClient(client)
        self._users = UsersClient(client)

    @property
    def search(self) -> SearchClient:
        """Access search endpoints.

        Returns:
            SearchClient for searching posts, subreddits, users, and domains.

        Example:
            ```python
            results = await client.reddit.search.posts(
                "python type hints",
                sort="top",
                time_filter="month",
            )
            ```
        """
        return self._search

    @property
    def posts(self) -> PostsClient:
        """Access post endpoints.

        Returns:
            PostsClient for fetching trending posts, post details, and comments.

        Example:
            ```python
            detail = await client.reddit.posts.get("python", "abc123")
            print(f"{detail.post.title}: {detail.post.score} pts")
            ```
        """
        return self._posts

    @property
    def subreddits(self) -> SubredditsClient:
        """Access subreddit endpoints.

        Returns:
            SubredditsClient for subreddit metadata, posts, rules, and wiki.

        Example:
            ```python
            info = await client.reddit.subreddits.get("python")
            rules = await client.reddit.subreddits.rules("python")
            posts = await client.reddit.subreddits.posts("python", sort="hot")
            ```
        """
        return self._subreddits

    @property
    def users(self) -> UsersClient:
        """Access user endpoints.

        Returns:
            UsersClient for fetching user profiles, posts, comments, and trophies.

        Example:
            ```python
            profile = await client.reddit.users.get("spez")
            posts = await client.reddit.users.posts("spez")
            trophies = await client.reddit.users.trophies("spez")
            ```
        """
        return self._users
