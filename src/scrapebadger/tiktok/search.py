"""TikTok Search API client.

Provides methods for general search and keyword search of videos, hashtags,
and users.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.tiktok.models import (
    HashtagSearchResponse,
    UserSearchResponse,
    VideoListResponse,
)

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class SearchClient:
    """Client for TikTok search endpoints (general, videos, hashtags, users).

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            results = await client.tiktok.search.general("cooking")
            for v in results.videos:
                print(v.description)

            users = await client.tiktok.search.users("gordon ramsay")
            for u in users.users:
                print(u.unique_id)
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize search client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def general(
        self,
        query: str,
        *,
        region: str = "US",
        count: int = 20,
        cursor: str | None = None,
    ) -> VideoListResponse:
        """General TikTok search — video results from the Top feed.

        Args:
            query: Search keyword.
            region: Content region. Defaults to "US".
            count: Number of results to return (1-50). Defaults to 20.
            cursor: Pagination cursor from a prior response's pagination.cursor;
                omit for the first page.

        Returns:
            Video list response with results and pagination metadata.
        """
        params: dict[str, Any] = {
            "query": query,
            "region": region,
            "count": count,
            "cursor": cursor,
        }
        response = await self._client.get("/v1/tiktok/search", params=params)
        return VideoListResponse.model_validate(response)

    async def videos(
        self,
        query: str,
        *,
        region: str = "US",
        count: int = 20,
        cursor: str | None = None,
    ) -> VideoListResponse:
        """Search TikTok videos by keyword.

        Args:
            query: Search keyword.
            region: Content region. Defaults to "US".
            count: Number of results to return (1-50). Defaults to 20.
            cursor: Pagination cursor from a prior response's pagination.cursor;
                omit for the first page.

        Returns:
            Video list response with matching videos and pagination metadata.
        """
        params: dict[str, Any] = {
            "query": query,
            "region": region,
            "count": count,
            "cursor": cursor,
        }
        response = await self._client.get("/v1/tiktok/search/videos", params=params)
        return VideoListResponse.model_validate(response)

    async def hashtags(
        self,
        query: str,
        *,
        region: str = "US",
        count: int = 20,
        cursor: str | None = None,
    ) -> HashtagSearchResponse:
        """Search TikTok hashtags by keyword.

        Args:
            query: Search keyword.
            region: Content region. Defaults to "US".
            count: Number of results to return (1-50). Defaults to 20.
            cursor: Pagination cursor from a prior response's pagination.cursor;
                omit for the first page.

        Returns:
            Hashtag search response with matching hashtags and pagination metadata.
        """
        params: dict[str, Any] = {
            "query": query,
            "region": region,
            "count": count,
            "cursor": cursor,
        }
        response = await self._client.get("/v1/tiktok/search/hashtags", params=params)
        return HashtagSearchResponse.model_validate(response)

    async def users(
        self,
        query: str,
        *,
        region: str = "US",
        count: int = 20,
        cursor: str | None = None,
    ) -> UserSearchResponse:
        """Search TikTok users by keyword.

        Args:
            query: Search keyword.
            region: Content region. Defaults to "US".
            count: Number of results to return (1-50). Defaults to 20.
            cursor: Pagination cursor from a prior response's pagination.cursor;
                omit for the first page.

        Returns:
            User search response with matching authors and pagination metadata.
        """
        params: dict[str, Any] = {
            "query": query,
            "region": region,
            "count": count,
            "cursor": cursor,
        }
        response = await self._client.get("/v1/tiktok/search/users", params=params)
        return UserSearchResponse.model_validate(response)
