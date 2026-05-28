"""Reddit Posts API client.

Provides methods for fetching individual posts, their comments,
trending posts, and cross-post duplicates.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.reddit.models import (
    PostCommentsResponse,
    PostDetailResponse,
    PostDuplicatesResponse,
    TrendingPostsResponse,
)

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class PostsClient:
    """Client for Reddit post endpoints.

    Provides async methods for fetching post details, comments,
    trending posts, and duplicate submissions.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            # Get trending posts
            trending = await client.reddit.posts.trending()
            for post in trending.posts:
                print(f"{post.title} ({post.score} pts)")

            # Get a specific post
            detail = await client.reddit.posts.get("python", "abc123")
            print(detail.post.title)

            # Get post comments
            comments = await client.reddit.posts.comments("python", "abc123")
            for comment in comments.comments:
                print(f"  {comment.author}: {comment.body[:80]}")
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize posts client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def trending(
        self,
        *,
        limit: int = 25,
        after: str | None = None,
    ) -> TrendingPostsResponse:
        """Get currently trending Reddit posts.

        Args:
            limit: Number of posts to return (1-100). Defaults to 25.
            after: Pagination cursor from a previous response.

        Returns:
            TrendingPostsResponse with trending posts.

        Raises:
            AuthenticationError: If the API key is invalid.

        Example:
            ```python
            result = await client.reddit.posts.trending(limit=10)
            for post in result.posts:
                print(f"r/{post.subreddit}: {post.title}")
            ```
        """
        params: dict[str, Any] = {
            "limit": limit,
            "after": after,
        }
        response = await self._client.get("/v1/reddit/posts/trending", params=params)
        return TrendingPostsResponse.model_validate(response)

    async def get(
        self,
        post_id: str,
    ) -> PostDetailResponse:
        """Get a specific Reddit post by post ID.

        Args:
            post_id: Post ID (base-36 string, e.g. "abc123"), without the
                t3_ prefix.

        Returns:
            PostDetailResponse with full post data.

        Raises:
            NotFoundError: If the post doesn't exist.
            AuthenticationError: If the API key is invalid.

        Example:
            ```python
            result = await client.reddit.posts.get("abc123")
            post = result.post
            print(f"{post.title}: {post.score} pts, {post.num_comments} comments")
            ```
        """
        response = await self._client.get(f"/v1/reddit/posts/{post_id}")
        return PostDetailResponse.model_validate(response)

    async def comments(
        self,
        post_id: str,
        *,
        sort: str = "best",
        limit: int = 25,
        depth: int | None = None,
        after: str | None = None,
    ) -> PostCommentsResponse:
        """Get comments for a Reddit post.

        Args:
            post_id: Post ID (base-36 string, e.g. "abc123"), without the
                t3_ prefix.
            sort: Comment sort order — "best", "top", "new", "controversial",
                "old", "qa". Defaults to "best".
            limit: Number of top-level comments (1-500). Defaults to 25.
            depth: Maximum comment tree depth to fetch. None means no limit.
            after: Pagination cursor from a previous response.

        Returns:
            PostCommentsResponse with comments and the parent post.

        Raises:
            NotFoundError: If the post doesn't exist.
            AuthenticationError: If the API key is invalid.

        Example:
            ```python
            result = await client.reddit.posts.comments(
                "abc123",
                sort="top",
                limit=100,
            )
            print(f"{len(result.comments)} top-level comments")
            for comment in result.comments:
                print(f"  u/{comment.author} ({comment.score} pts): {comment.body[:80]}")
            ```
        """
        params: dict[str, Any] = {
            "sort": sort,
            "limit": limit,
            "depth": depth,
            "after": after,
        }
        response = await self._client.get(
            f"/v1/reddit/posts/{post_id}/comments",
            params=params,
        )
        return PostCommentsResponse.model_validate(response)

    async def duplicates(
        self,
        post_id: str,
        *,
        limit: int = 25,
        after: str | None = None,
    ) -> PostDuplicatesResponse:
        """Get cross-posts and duplicate submissions of a Reddit post.

        Args:
            post_id: Post ID (base-36 string, e.g. "abc123").
            limit: Number of results (1-100). Defaults to 25.
            after: Pagination cursor from a previous response.

        Returns:
            PostDuplicatesResponse with duplicate/cross-posted posts.

        Raises:
            NotFoundError: If the post doesn't exist.
            AuthenticationError: If the API key is invalid.

        Example:
            ```python
            result = await client.reddit.posts.duplicates("abc123")
            print(f"Found in {len(result.posts)} subreddits")
            for post in result.posts:
                print(f"  r/{post.subreddit}: {post.title}")
            ```
        """
        params: dict[str, Any] = {
            "limit": limit,
            "after": after,
        }
        response = await self._client.get(
            f"/v1/reddit/posts/{post_id}/duplicates",
            params=params,
        )
        return PostDuplicatesResponse.model_validate(response)
