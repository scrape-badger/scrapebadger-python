"""YouTube Search API client.

Provides methods for keyword search, YouTube Music search, keyword autocomplete,
hashtag feeds, and the guest home feed.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.youtube.models import (
    AutocompleteResponse,
    HashtagResponse,
    HomeResponse,
    SearchResponse,
)

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class SearchClient:
    """Client for YouTube search, music search, autocomplete, hashtag, and home feeds.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            results = await client.youtube.search.search("lofi hip hop")
            for r in results.results:
                print(f"{r.position}. {r.title}")

            songs = await client.youtube.search.music("daft punk")

            suggestions = await client.youtube.search.autocomplete("lofi")
            for s in suggestions.suggestions:
                print(s)
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize search client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def search(
        self,
        query: str,
        *,
        type: str | None = None,
        sort_by: str | None = None,
        upload_date: str | None = None,
        duration: str | None = None,
        features: str | None = None,
        gl: str | None = None,
        hl: str | None = None,
        continuation: str | None = None,
    ) -> SearchResponse:
        """Search YouTube for videos, channels, and playlists.

        Args:
            query: Search keywords.
            type: Restrict result type ("video", "channel", "playlist", "movie", "all").
            sort_by: Sort order ("relevance", "date", "views", "rating").
            upload_date: Upload-date filter ("hour", "today", "week", "month", "year").
            duration: Duration filter ("short", "medium", "long").
            features: Comma list of feature filters
                (hd,4k,360,vr180,3d,hdr,cc,subtitles,live,location).
            gl: Content region (US, GB, DE…).
            hl: UI language.
            continuation: Pagination token from a previous page.

        Returns:
            Search response with matching results, chips, and a continuation token.

        Raises:
            AuthenticationError: If the API key is invalid.
            ValidationError: If the parameters are invalid.

        Example:
            ```python
            results = await client.youtube.search.search(
                "python tutorial",
                type="video",
                sort_by="views",
                upload_date="month",
            )
            ```
        """
        params: dict[str, Any] = {
            "query": query,
            "type": type,
            "sort_by": sort_by,
            "upload_date": upload_date,
            "duration": duration,
            "features": features,
            "gl": gl,
            "hl": hl,
            "continuation": continuation,
        }
        response = await self._client.get("/v1/youtube/search", params=params)
        return SearchResponse.model_validate(response)

    async def music(
        self,
        query: str,
        *,
        gl: str | None = None,
        hl: str | None = None,
        continuation: str | None = None,
    ) -> SearchResponse:
        """Search YouTube Music (songs/albums/artists/playlists).

        Args:
            query: Search keywords.
            gl: Content region (US, GB, DE…).
            hl: UI language.
            continuation: Pagination token from a previous page.

        Returns:
            Search response from the WEB_REMIX (YouTube Music) client.

        Example:
            ```python
            results = await client.youtube.search.music("daft punk")
            ```
        """
        params: dict[str, Any] = {
            "query": query,
            "gl": gl,
            "hl": hl,
            "continuation": continuation,
        }
        response = await self._client.get("/v1/youtube/music/search", params=params)
        return SearchResponse.model_validate(response)

    async def autocomplete(
        self,
        query: str,
        *,
        gl: str | None = None,
        hl: str | None = None,
    ) -> AutocompleteResponse:
        """Get YouTube keyword autocomplete suggestions.

        Args:
            query: Partial search query prefix.
            gl: Content region (US, GB, DE…).
            hl: UI language.

        Returns:
            Autocomplete response with keyword suggestions.

        Example:
            ```python
            result = await client.youtube.search.autocomplete("lofi")
            for s in result.suggestions:
                print(s)
            ```
        """
        params: dict[str, Any] = {"query": query, "gl": gl, "hl": hl}
        response = await self._client.get("/v1/youtube/autocomplete", params=params)
        return AutocompleteResponse.model_validate(response)

    async def hashtag(
        self,
        tag: str,
        *,
        gl: str | None = None,
        hl: str | None = None,
        continuation: str | None = None,
    ) -> HashtagResponse:
        """List videos published under a hashtag.

        Args:
            tag: The hashtag (with or without a leading ``#``).
            gl: Content region (US, GB, DE…).
            hl: UI language.
            continuation: Pagination token from a previous page.

        Returns:
            Hashtag response with results and a continuation token.

        Example:
            ```python
            result = await client.youtube.search.hashtag("shorts")
            ```
        """
        params: dict[str, Any] = {"gl": gl, "hl": hl, "continuation": continuation}
        response = await self._client.get(f"/v1/youtube/hashtags/{tag}", params=params)
        return HashtagResponse.model_validate(response)

    async def home(
        self,
        *,
        gl: str | None = None,
        hl: str | None = None,
        continuation: str | None = None,
    ) -> HomeResponse:
        """Get the guest home / recommendations feed (best-effort).

        Args:
            gl: Content region (US, GB, DE…).
            hl: UI language.
            continuation: Pagination token from a previous page.

        Returns:
            Home response with recommended results and a continuation token.

        Example:
            ```python
            feed = await client.youtube.search.home(gl="US")
            ```
        """
        params: dict[str, Any] = {"gl": gl, "hl": hl, "continuation": continuation}
        response = await self._client.get("/v1/youtube/home", params=params)
        return HomeResponse.model_validate(response)
