"""Reddit Subreddits API client.

Provides methods for fetching subreddit metadata, posts, rules,
moderators, wiki pages, and subreddit listings.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.reddit.models import (
    SubredditDetailResponse,
    SubredditPostsResponse,
    SubredditRulesResponse,
    SubredditsListResponse,
    SubredditWikiPageResponse,
    SubredditWikiPagesResponse,
)

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class SubredditsClient:
    """Client for Reddit subreddit endpoints.

    Provides async methods for fetching subreddit information and content.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            # Get subreddit info
            info = await client.reddit.subreddits.get("python")
            print(f"r/python: {info.subreddit.subscribers:,} members")

            # Get hot posts
            posts = await client.reddit.subreddits.posts("python", sort="hot")
            for post in posts.posts:
                print(f"  {post.title} ({post.score} pts)")

            # Get rules
            rules = await client.reddit.subreddits.rules("python")
            for rule in rules.rules:
                print(f"  {rule.short_name}")
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize subreddits client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def get(self, subreddit: str) -> SubredditDetailResponse:
        """Get metadata for a subreddit.

        Args:
            subreddit: Subreddit name (without r/ prefix).

        Returns:
            SubredditDetailResponse with full subreddit data.

        Raises:
            NotFoundError: If the subreddit doesn't exist.
            AuthenticationError: If the API key is invalid.

        Example:
            ```python
            result = await client.reddit.subreddits.get("python")
            sub = result.subreddit
            print(f"r/{sub.name}: {sub.subscribers:,} subscribers")
            print(f"Active users: {sub.active_user_count}")
            ```
        """
        response = await self._client.get(f"/v1/reddit/subreddits/{subreddit}")
        return SubredditDetailResponse.model_validate(response)

    async def posts(
        self,
        subreddit: str,
        *,
        sort: str = "hot",
        time_filter: str | None = None,
        limit: int = 25,
        after: str | None = None,
        before: str | None = None,
    ) -> SubredditPostsResponse:
        """Get posts from a subreddit.

        Args:
            subreddit: Subreddit name (without r/ prefix).
            sort: Sort order — "hot", "new", "top", "rising", "controversial".
                Defaults to "hot".
            time_filter: Time window for "top" and "controversial" sort —
                "hour", "day", "week", "month", "year", "all". Optional.
            limit: Number of posts (1-100). Defaults to 25.
            after: Pagination cursor from a previous response.
            before: Pagination cursor for the previous page.

        Returns:
            SubredditPostsResponse with posts and pagination cursors.

        Raises:
            NotFoundError: If the subreddit doesn't exist.
            AuthenticationError: If the API key is invalid.

        Example:
            ```python
            result = await client.reddit.subreddits.posts(
                "python",
                sort="top",
                time_filter="week",
                limit=50,
            )
            for post in result.posts:
                print(f"  {post.title} — {post.score} pts")
            ```
        """
        params: dict[str, Any] = {
            "sort": sort,
            "time_filter": time_filter,
            "limit": limit,
            "after": after,
            "before": before,
        }
        response = await self._client.get(
            f"/v1/reddit/subreddits/{subreddit}/posts",
            params=params,
        )
        return SubredditPostsResponse.model_validate(response)

    async def rules(self, subreddit: str) -> SubredditRulesResponse:
        """Get the posting rules for a subreddit.

        Args:
            subreddit: Subreddit name (without r/ prefix).

        Returns:
            SubredditRulesResponse with list of rules.

        Raises:
            NotFoundError: If the subreddit doesn't exist.
            AuthenticationError: If the API key is invalid.

        Example:
            ```python
            result = await client.reddit.subreddits.rules("learnpython")
            for rule in result.rules:
                print(f"  {rule.priority}. {rule.short_name}")
            ```
        """
        response = await self._client.get(f"/v1/reddit/subreddits/{subreddit}/rules")
        return SubredditRulesResponse.model_validate(response)

    async def wiki_pages(self, subreddit: str) -> SubredditWikiPagesResponse:
        """Get the list of wiki page names for a subreddit.

        Args:
            subreddit: Subreddit name (without r/ prefix).

        Returns:
            SubredditWikiPagesResponse with page name list.

        Raises:
            NotFoundError: If the subreddit doesn't exist.
            AuthenticationError: If the API key is invalid.

        Example:
            ```python
            result = await client.reddit.subreddits.wiki_pages("python")
            for page_name in result.pages:
                print(f"  {page_name}")
            ```
        """
        response = await self._client.get(f"/v1/reddit/subreddits/{subreddit}/wiki")
        return SubredditWikiPagesResponse.model_validate(response)

    async def wiki_page(
        self,
        subreddit: str,
        page: str,
    ) -> SubredditWikiPageResponse:
        """Get the content of a specific subreddit wiki page.

        Args:
            subreddit: Subreddit name (without r/ prefix).
            page: Wiki page name (e.g. "rules", "faq", "index").

        Returns:
            SubredditWikiPageResponse with page content.

        Raises:
            NotFoundError: If the subreddit or page doesn't exist.
            AuthenticationError: If the API key is invalid.

        Example:
            ```python
            result = await client.reddit.subreddits.wiki_page("python", "rules")
            print(result.page.content_md)
            ```
        """
        response = await self._client.get(f"/v1/reddit/subreddits/{subreddit}/wiki/{page}")
        return SubredditWikiPageResponse.model_validate(response)

    async def popular(
        self,
        *,
        limit: int = 25,
        after: str | None = None,
    ) -> SubredditsListResponse:
        """Get currently popular subreddits.

        Args:
            limit: Number of subreddits (1-100). Defaults to 25.
            after: Pagination cursor from a previous response.

        Returns:
            SubredditsListResponse with popular subreddits.

        Raises:
            AuthenticationError: If the API key is invalid.

        Example:
            ```python
            result = await client.reddit.subreddits.popular(limit=10)
            for sub in result.subreddits:
                print(f"r/{sub.name}: {sub.subscribers:,} members")
            ```
        """
        params: dict[str, Any] = {
            "limit": limit,
            "after": after,
        }
        response = await self._client.get("/v1/reddit/subreddits/popular", params=params)
        return SubredditsListResponse.model_validate(response)

    async def new(
        self,
        *,
        limit: int = 25,
        after: str | None = None,
    ) -> SubredditsListResponse:
        """Get newly created subreddits.

        Args:
            limit: Number of subreddits (1-100). Defaults to 25.
            after: Pagination cursor from a previous response.

        Returns:
            SubredditsListResponse with newly created subreddits.

        Raises:
            AuthenticationError: If the API key is invalid.

        Example:
            ```python
            result = await client.reddit.subreddits.new()
            for sub in result.subreddits:
                print(f"r/{sub.name}: created {sub.created_utc}")
            ```
        """
        params: dict[str, Any] = {
            "limit": limit,
            "after": after,
        }
        response = await self._client.get("/v1/reddit/subreddits/new", params=params)
        return SubredditsListResponse.model_validate(response)
