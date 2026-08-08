"""DuckDuckGo Media Search API client (images, news, videos)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.duckduckgo.models import (
    ImageResponse,
    NewsResponse,
    VideoResponse,
)

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class MediaClient:
    """Client for DuckDuckGo image, news, and video search endpoints.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            images = await client.duckduckgo.media.images("golden retriever")
            news = await client.duckduckgo.media.news("elections")
            videos = await client.duckduckgo.media.videos("guitar tutorial")
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize media client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def images(
        self,
        query: str,
        *,
        region: str = "wt-wt",
        safesearch: str = "moderate",
        page: int = 1,
        size: str | None = None,
        color: str | None = None,
        image_type: str | None = None,
        layout: str | None = None,
        license: str | None = None,
    ) -> ImageResponse:
        """Search DuckDuckGo images.

        Args:
            query: Search keywords, e.g. ``"golden retriever"``.
            region: Region code. Default ``"wt-wt"``.
            safesearch: ``"on"``, ``"moderate"``, or ``"off"``.
            page: Page number.
            size: Size filter — ``"Small"``, ``"Medium"``, ``"Large"``, ``"Wallpaper"``.
            color: Colour filter, e.g. ``"Red"``, ``"Monochrome"``.
            image_type: Type filter — ``"photo"``, ``"clipart"``, ``"gif"``,
                ``"transparent"``, ``"line"``.
            layout: Layout filter — ``"Square"``, ``"Tall"``, ``"Wide"``.
            license: Licence filter, e.g. ``"Public"``, ``"Share"``, ``"Modify"``.

        Returns:
            ImageResponse with the image results.

        Example:
            ```python
            result = await client.duckduckgo.media.images(
                "sunset", size="Large", color="Orange"
            )
            for img in result.results:
                print(img.image, img.width, img.height)
            ```
        """
        params: dict[str, Any] = {
            "query": query,
            "region": region,
            "safesearch": safesearch,
            "page": page,
            "size": size,
            "color": color,
            "image_type": image_type,
            "layout": layout,
            "license": license,
        }
        response = await self._client.get("/v1/duckduckgo/images", params=params)
        return ImageResponse.model_validate(response)

    async def news(
        self,
        query: str,
        *,
        region: str = "wt-wt",
        safesearch: str = "moderate",
        timelimit: str = "",
        page: int = 1,
    ) -> NewsResponse:
        """Search DuckDuckGo news.

        Args:
            query: Search keywords, e.g. ``"elections"``.
            region: Region code. Default ``"wt-wt"``.
            safesearch: ``"on"``, ``"moderate"``, or ``"off"``.
            timelimit: Recency filter — ``"d"``, ``"w"``, ``"m"``, or ``""``.
            page: Page number.

        Returns:
            NewsResponse with the news articles.

        Example:
            ```python
            result = await client.duckduckgo.media.news("markets", timelimit="d")
            for a in result.results:
                print(a.title, a.source, a.relative_time)
            ```
        """
        params: dict[str, Any] = {
            "query": query,
            "region": region,
            "safesearch": safesearch,
            "timelimit": timelimit,
            "page": page,
        }
        response = await self._client.get("/v1/duckduckgo/news", params=params)
        return NewsResponse.model_validate(response)

    async def videos(
        self,
        query: str,
        *,
        region: str = "wt-wt",
        safesearch: str = "moderate",
        page: int = 1,
        duration: str | None = None,
        resolution: str | None = None,
    ) -> VideoResponse:
        """Search DuckDuckGo videos.

        Args:
            query: Search keywords, e.g. ``"guitar tutorial"``.
            region: Region code. Default ``"wt-wt"``.
            safesearch: ``"on"``, ``"moderate"``, or ``"off"``.
            page: Page number.
            duration: Duration filter — ``"short"``, ``"medium"``, ``"long"``.
            resolution: Resolution filter — ``"high"``, ``"standard"``.

        Returns:
            VideoResponse with the video results.

        Example:
            ```python
            result = await client.duckduckgo.media.videos(
                "python tutorial", duration="short"
            )
            for v in result.results:
                print(v.title, v.publisher, v.view_count)
            ```
        """
        params: dict[str, Any] = {
            "query": query,
            "region": region,
            "safesearch": safesearch,
            "page": page,
            "duration": duration,
            "resolution": resolution,
        }
        response = await self._client.get("/v1/duckduckgo/videos", params=params)
        return VideoResponse.model_validate(response)
