"""Reddit Search API client.

Provides methods for searching Reddit posts, subreddits, users, and
domain-linked submissions.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.reddit.models import (
    SearchPostsResponse,
    SearchUsersResponse,
    SubredditsListResponse,
)

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class SearchClient:
    """Client for Reddit search endpoints.

    Provides async methods for searching across Reddit's content.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            # Search posts
            results = await client.reddit.search.posts("python asyncio")
            for post in results.posts:
                print(f"r/{post.subreddit}: {post.title} ({post.score} pts)")

            # Search subreddits
            subs = await client.reddit.search.subreddits("programming")
            for sub in subs.subreddits:
                print(f"r/{sub.name}: {sub.subscribers:,} members")

            # Search posts from a domain
            links = await client.reddit.search.domain_posts("github.com")
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize search client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def posts(
        self,
        query: str,
        *,
        subreddit: str | None = None,
        sort: str = "relevance",
        time_filter: str = "all",
        limit: int = 25,
        after: str | None = None,
        before: str | None = None,
    ) -> SearchPostsResponse:
        """Search Reddit posts.

        Args:
            query: Search query string.
            subreddit: Restrict search to a specific subreddit (without r/ prefix).
            sort: Sort order — "relevance", "hot", "top", "new", "comments".
                Defaults to "relevance".
            time_filter: Time window — "hour", "day", "week", "month", "year",
                "all". Defaults to "all".
            limit: Number of results (1-100). Defaults to 25.
            after: Pagination cursor from a previous response.
            before: Pagination cursor for the previous page.

        Returns:
            SearchPostsResponse with matching posts and pagination cursors.

        Raises:
            AuthenticationError: If the API key is invalid.
            ValidationError: If the parameters are invalid.

        Example:
            ```python
            results = await client.reddit.search.posts(
                "python type hints",
                subreddit="learnpython",
                sort="top",
                time_filter="month",
                limit=50,
            )
            print(f"Found {results.count} posts")
            for post in results.posts:
                print(f"  {post.title} — {post.score} pts")
            ```
        """
        params: dict[str, Any] = {
            "query": query,
            "subreddit": subreddit,
            "sort": sort,
            "time_filter": time_filter,
            "limit": limit,
            "after": after,
            "before": before,
        }
        response = await self._client.get("/v1/reddit/search/posts", params=params)
        return SearchPostsResponse.model_validate(response)

    async def subreddits(
        self,
        query: str,
        *,
        limit: int = 25,
        after: str | None = None,
    ) -> SubredditsListResponse:
        """Search Reddit subreddits.

        Args:
            query: Search query string.
            limit: Number of results (1-100). Defaults to 25.
            after: Pagination cursor from a previous response.

        Returns:
            SubredditsListResponse with matching subreddits.

        Raises:
            AuthenticationError: If the API key is invalid.

        Example:
            ```python
            results = await client.reddit.search.subreddits("machine learning")
            for sub in results.subreddits:
                print(f"r/{sub.name}: {sub.subscribers:,} members")
            ```
        """
        params: dict[str, Any] = {
            "query": query,
            "limit": limit,
            "after": after,
        }
        response = await self._client.get("/v1/reddit/search/subreddits", params=params)
        return SubredditsListResponse.model_validate(response)

    async def users(
        self,
        query: str,
        *,
        limit: int = 25,
        after: str | None = None,
    ) -> SearchUsersResponse:
        """Search Reddit users.

        Args:
            query: Search query string (matches usernames).
            limit: Number of results (1-100). Defaults to 25.
            after: Pagination cursor from a previous response.

        Returns:
            SearchUsersResponse with matching user accounts.

        Raises:
            AuthenticationError: If the API key is invalid.

        Example:
            ```python
            results = await client.reddit.search.users("python")
            for user in results.users:
                print(f"u/{user.name}: {user.total_karma:,} karma")
            ```
        """
        params: dict[str, Any] = {
            "query": query,
            "limit": limit,
            "after": after,
        }
        response = await self._client.get("/v1/reddit/search/users", params=params)
        return SearchUsersResponse.model_validate(response)

    async def domain_posts(
        self,
        domain: str,
        *,
        sort: str = "relevance",
        time_filter: str = "all",
        limit: int = 25,
        after: str | None = None,
    ) -> SearchPostsResponse:
        """Search Reddit posts linking to a specific domain.

        Args:
            domain: Domain to search for (e.g. "github.com", "nytimes.com").
            sort: Sort order — "relevance", "hot", "top", "new". Defaults to
                "relevance".
            time_filter: Time window — "hour", "day", "week", "month", "year",
                "all". Defaults to "all".
            limit: Number of results (1-100). Defaults to 25.
            after: Pagination cursor from a previous response.

        Returns:
            SearchPostsResponse with posts that link to the domain.

        Raises:
            AuthenticationError: If the API key is invalid.

        Example:
            ```python
            results = await client.reddit.search.domain_posts(
                "github.com",
                sort="top",
                time_filter="week",
            )
            for post in results.posts:
                print(f"r/{post.subreddit}: {post.title}")
            ```
        """
        params: dict[str, Any] = {
            "domain": domain,
            "sort": sort,
            "time_filter": time_filter,
            "limit": limit,
            "after": after,
        }
        response = await self._client.get("/v1/reddit/search/domain", params=params)
        return SearchPostsResponse.model_validate(response)
