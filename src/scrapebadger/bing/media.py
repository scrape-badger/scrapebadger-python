"""Bing Media API client.

Image search and video search.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.bing.models import ImagesResponse, VideosResponse

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient
    from scrapebadger.bing.search import SafeSearch


class MediaClient:
    """Client for Bing image and video search endpoints.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            images = await client.bing.media.images("cats")
            for img in images.results:
                print(img.image_url, img.width, img.height)

            videos = await client.bing.media.videos("cats")
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
        market: str = "en-US",
        count: int = 35,
        safe_search: SafeSearch | None = None,
    ) -> ImagesResponse:
        """Search Bing images.

        Args:
            query: Search keywords, e.g. ``"cats"``.
            market: Bing market code, e.g. ``"en-US"``.
            count: Number of images to return.
            safe_search: Adult-content filter — ``"off"``, ``"moderate"``
                or ``"strict"``.

        Returns:
            ImagesResponse with full-size image URLs, thumbnails, pixel
            dimensions and the source page each image came from.

        Example:
            ```python
            images = await client.bing.media.images("cats")
            for img in images.results:
                print(img.image_url, img.source_url)
            ```
        """
        params: dict[str, Any] = {
            "query": query,
            "market": market,
            "count": count,
            "safe_search": safe_search,
        }
        response = await self._client.get("/v1/bing/images", params=params)
        return ImagesResponse.model_validate(response)

    async def videos(
        self,
        query: str,
        *,
        market: str = "en-US",
        count: int = 35,
        safe_search: SafeSearch | None = None,
    ) -> VideosResponse:
        """Search Bing videos.

        Args:
            query: Search keywords, e.g. ``"cats"``.
            market: Bing market code, e.g. ``"en-US"``.
            count: Number of videos to return.
            safe_search: Adult-content filter — ``"off"``, ``"moderate"``
                or ``"strict"``.

        Returns:
            VideosResponse with video URLs, thumbnails, duration, publisher
            and view counts.

        Example:
            ```python
            videos = await client.bing.media.videos("cats")
            for v in videos.results:
                print(v.title, v.duration, v.views)
            ```
        """
        params: dict[str, Any] = {
            "query": query,
            "market": market,
            "count": count,
            "safe_search": safe_search,
        }
        response = await self._client.get("/v1/bing/videos", params=params)
        return VideosResponse.model_validate(response)
