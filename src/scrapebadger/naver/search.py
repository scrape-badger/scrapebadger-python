"""Naver Search API client.

Provides methods for the integrated SERP, autocomplete, and the news, blog,
web, cafe, Knowledge iN, image, video, and clip verticals.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.naver.models import (
    AutocompleteResponse,
    BlogResponse,
    CafeResponse,
    ClipResponse,
    ImageResponse,
    KinResponse,
    LocalSearchResponse,
    NewsResponse,
    SearchResponse,
    VideoResponse,
    WebSearchResponse,
)

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class SearchClient:
    """Client for Naver search and vertical SERP endpoints.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            results = await client.naver.search.search("커피머신")
            for item in results.results:
                print(f"{item.position}. {item.title}")

            suggestions = await client.naver.search.autocomplete("커피")
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
        page: int = 1,
        view: str | None = None,
    ) -> SearchResponse:
        """Integrated (nexearch) SERP: organic results + inline Place pack.

        Args:
            query: Search keywords.
            page: Result page, 1-based (1..40, clamped). Defaults to 1.
            view: Pass "more" for the extended (ur.all) view (page is 1..10).

        Returns:
            Search response with organic results, related searches, and places.
        """
        params: dict[str, Any] = {"query": query, "page": page, "view": view}
        response = await self._client.get("/v1/naver/search", params=params)
        return SearchResponse.model_validate(response)

    async def news(
        self,
        query: str,
        *,
        page: int = 1,
        sort: str = "relevance",
    ) -> NewsResponse:
        """Search the Naver news vertical.

        Args:
            query: Search keywords.
            page: Result page, 1-based (1..40). Defaults to 1.
            sort: Sort order ("relevance", "recent", or "old"). Defaults to "relevance".

        Returns:
            News response with matching results.
        """
        params: dict[str, Any] = {"query": query, "page": page, "sort": sort}
        response = await self._client.get("/v1/naver/news", params=params)
        return NewsResponse.model_validate(response)

    async def blog(
        self,
        query: str,
        *,
        page: int = 1,
    ) -> BlogResponse:
        """Search the Naver blog vertical.

        Args:
            query: Search keywords.
            page: Result page, 1-based (1..40). Defaults to 1.

        Returns:
            Blog response with matching results.
        """
        params: dict[str, Any] = {"query": query, "page": page}
        response = await self._client.get("/v1/naver/blog", params=params)
        return BlogResponse.model_validate(response)

    async def autocomplete(self, query: str) -> AutocompleteResponse:
        """Get search-box autocomplete suggestions.

        Args:
            query: Partial search term.

        Returns:
            Autocomplete response with keyword suggestions.
        """
        params: dict[str, Any] = {"query": query}
        response = await self._client.get("/v1/naver/autocomplete", params=params)
        return AutocompleteResponse.model_validate(response)

    async def local(
        self,
        query: str,
        *,
        start: int | None = None,
        display: int | None = None,
        x: float | None = None,
        y: float | None = None,
    ) -> LocalSearchResponse:
        """Search local businesses (map pack).

        Args:
            query: Search keywords.
            start: 1-based result offset (presence switches the result lane).
            display: Results per page (1..100).
            x: Longitude to bias results.
            y: Latitude to bias results.

        Returns:
            Local search response with place cards.
        """
        params: dict[str, Any] = {
            "query": query,
            "start": start,
            "display": display,
            "x": x,
            "y": y,
        }
        response = await self._client.get("/v1/naver/local", params=params)
        return LocalSearchResponse.model_validate(response)

    async def web(
        self,
        query: str,
        *,
        page: int = 1,
    ) -> WebSearchResponse:
        """Search the Naver web vertical (15 docs/page).

        Args:
            query: Search keywords.
            page: Result page, 1-based. Defaults to 1.

        Returns:
            Web search response with matching results.
        """
        params: dict[str, Any] = {"query": query, "page": page}
        response = await self._client.get("/v1/naver/search/web", params=params)
        return WebSearchResponse.model_validate(response)

    async def cafe(
        self,
        query: str,
        *,
        page: int = 1,
    ) -> CafeResponse:
        """Search the Naver Cafe vertical (30/page).

        Args:
            query: Search keywords.
            page: Result page, 1-based. Defaults to 1.

        Returns:
            Cafe response with matching results.
        """
        params: dict[str, Any] = {"query": query, "page": page}
        response = await self._client.get("/v1/naver/cafe", params=params)
        return CafeResponse.model_validate(response)

    async def kin(
        self,
        query: str,
        *,
        page: int = 1,
    ) -> KinResponse:
        """Search the Naver Knowledge iN vertical (10/page).

        Args:
            query: Search keywords.
            page: Result page, 1-based. Defaults to 1.

        Returns:
            Knowledge iN response with matching results.
        """
        params: dict[str, Any] = {"query": query, "page": page}
        response = await self._client.get("/v1/naver/kin", params=params)
        return KinResponse.model_validate(response)

    async def image(
        self,
        query: str,
        *,
        page: int = 1,
    ) -> ImageResponse:
        """Search the Naver image vertical (JSON API 100/page).

        Args:
            query: Search keywords.
            page: Result page, 1-based. Defaults to 1.

        Returns:
            Image response with matching results.
        """
        params: dict[str, Any] = {"query": query, "page": page}
        response = await self._client.get("/v1/naver/image", params=params)
        return ImageResponse.model_validate(response)

    async def video(
        self,
        query: str,
        *,
        page: int = 1,
    ) -> VideoResponse:
        """Search the Naver video vertical (/more pagination, step 48).

        Args:
            query: Search keywords.
            page: Result page, 1-based. Defaults to 1.

        Returns:
            Video response with matching results.
        """
        params: dict[str, Any] = {"query": query, "page": page}
        response = await self._client.get("/v1/naver/video", params=params)
        return VideoResponse.model_validate(response)

    async def clip(
        self,
        query: str,
        *,
        page: int = 1,
    ) -> ClipResponse:
        """Search the Naver clip vertical (/more pagination, step 24).

        Args:
            query: Search keywords.
            page: Result page, 1-based. Defaults to 1.

        Returns:
            Clip response with matching results.
        """
        params: dict[str, Any] = {"query": query, "page": page}
        response = await self._client.get("/v1/naver/clip", params=params)
        return ClipResponse.model_validate(response)
