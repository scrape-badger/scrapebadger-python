"""Baidu API client.

Baidu endpoints: search (web SERP), news (news vertical), images (image
search) and autocomplete (search-box suggestions). All methods are async and
return strongly-typed Pydantic models.

Baidu is China's #1 search engine (~60% of the market). Every request is
served from ScrapeBadger's own exits — no China-based proxy of your own is
needed.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from scrapebadger.baidu.models import (
    AutocompleteResponse,
    ImagesResponse,
    NewsResponse,
    SearchResponse,
)

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient

Language = Literal["all", "zh-cn", "zh-tw"]
NewsSort = Literal["relevance", "time"]


class BaiduClient:
    """Client for all Baidu API operations.

    Baidu is China's dominant search engine. Organic and news results carry
    the **real target URL** in ``url`` (decoded from Baidu's ``mu``
    attribute), not just the ``baidu.com/link?url=`` tracking redirect that
    competing APIs return — ``baidu_url`` holds that redirect separately.

    Example:
        ```python
        from scrapebadger import ScrapeBadger

        async with ScrapeBadger(api_key="your-key") as client:
            # Web search
            results = await client.baidu.search("咖啡机")
            for r in results.results:
                print(f"{r.position}. {r.title} — {r.url}")

            # News
            news = await client.baidu.news("人工智能", sort="time")

            # Images
            images = await client.baidu.images("猫")

            # Search-box suggestions
            suggestions = await client.baidu.autocomplete("咖啡")
        ```

    Note:
        This client is not instantiated directly. Instead, access it through
        the `baidu` property of the main `ScrapeBadger` client.
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize Baidu client.

        Args:
            client: The base HTTP client for making API requests.
        """
        self._client = client

    async def search(
        self,
        query: str,
        *,
        page: int = 1,
        num: int = 10,
        language: Language = "all",
        time_from: int | None = None,
        time_to: int | None = None,
    ) -> SearchResponse:
        """Search baidu.com — the web SERP.

        Costs 5 credits.

        Args:
            query: Search keywords, e.g. ``"咖啡机"`` or ``"coffee machine"``.
            page: Result page, 1-76. Baidu's SERP stops serving past ~76 pages
                regardless of the total it reports, so the API clamps there.
            num: Results per page, 1-50 (Baidu's own cap).
            language: Restrict result language — ``"all"``, ``"zh-cn"``
                (simplified Chinese) or ``"zh-tw"`` (traditional Chinese).
            time_from: Unix timestamp — only results published after this.
            time_to: Unix timestamp — only results published before this.

        Returns:
            SearchResponse with organic results and Baidu's related searches.

        Raises:
            AuthenticationError: If the API key is invalid.
            ValidationError: If the parameters are invalid.

        Example:
            ```python
            results = await client.baidu.search("咖啡机", num=20, language="zh-cn")
            for r in results.results:
                # r.url is the real destination, r.baidu_url the redirect
                print(r.title, r.url, r.date_at)
            ```
        """
        params: dict[str, Any] = {
            "query": query,
            "page": page,
            "num": num,
            "language": language,
            "time_from": time_from,
            "time_to": time_to,
        }
        response = await self._client.get("/v1/baidu/search", params=params)
        return SearchResponse.model_validate(response)

    async def news(
        self,
        query: str,
        *,
        page: int = 1,
        sort: NewsSort = "relevance",
    ) -> NewsResponse:
        """Search the Baidu news vertical.

        Costs 5 credits.

        Args:
            query: Search keywords, e.g. ``"人工智能"``.
            page: Result page, 1-76.
            sort: Order by ``"relevance"`` or ``"time"`` (most recent first).

        Returns:
            NewsResponse with articles carrying publisher, date and real URLs.

        Raises:
            AuthenticationError: If the API key is invalid.
            ValidationError: If the parameters are invalid.

        Example:
            ```python
            news = await client.baidu.news("人工智能", sort="time")
            for article in news.results:
                print(article.source, article.date_at, article.title)
            ```
        """
        params: dict[str, Any] = {"query": query, "page": page, "sort": sort}
        response = await self._client.get("/v1/baidu/news", params=params)
        return NewsResponse.model_validate(response)

    async def images(self, query: str, *, page: int = 1) -> ImagesResponse:
        """Search Baidu images.

        Costs 5 credits.

        Args:
            query: Search keywords, e.g. ``"猫"``.
            page: Result page, 1-50. Baidu serves 30 images per page.

        Returns:
            ImagesResponse with full-size image URLs, Baidu-hosted thumbnail
            copies, pixel dimensions and the source page each image came from.

        Raises:
            AuthenticationError: If the API key is invalid.
            ValidationError: If the parameters are invalid.

        Example:
            ```python
            images = await client.baidu.images("猫")
            for img in images.results:
                print(img.image_url, img.width, img.height, img.from_url)
            ```
        """
        params: dict[str, Any] = {"query": query, "page": page}
        response = await self._client.get("/v1/baidu/images", params=params)
        return ImagesResponse.model_validate(response)

    async def autocomplete(self, query: str) -> AutocompleteResponse:
        """Baidu search-box suggestions — the cheapest call in this API.

        Costs 1 credit.

        Args:
            query: Partial search term, e.g. ``"咖啡"`` or ``"coff"``.

        Returns:
            AutocompleteResponse with Baidu's suggestions for the term.

        Raises:
            AuthenticationError: If the API key is invalid.
            ValidationError: If the parameters are invalid.

        Example:
            ```python
            result = await client.baidu.autocomplete("咖啡")
            for s in result.suggestions:
                print(s.query)
            ```
        """
        params: dict[str, Any] = {"query": query}
        response = await self._client.get("/v1/baidu/autocomplete", params=params)
        return AutocompleteResponse.model_validate(response)
