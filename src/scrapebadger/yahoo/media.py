"""Yahoo Media API client.

Image search and video search.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.yahoo.models import ImagesResponse, VideosResponse

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class MediaClient:
    """Client for Yahoo image and video search endpoints.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            images = await client.yahoo.media.images("cats")
            for img in images.results:
                print(img.image_url, img.width, img.height)

            videos = await client.yahoo.media.videos("cats")
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
        market: str = "us",
        count: int = 30,
    ) -> ImagesResponse:
        """Search Yahoo images.

        Yahoo renders ~60 tiles server-side with no native page-size
        parameter, so ``count`` trims the list rather than paginating.

        Args:
            query: Search keywords, e.g. ``"cats"``.
            market: Yahoo market code, e.g. ``"us"``.
            count: Number of images to return (1-100).

        Returns:
            ImagesResponse with full-size image URLs, thumbnails, pixel
            dimensions and the source page each image came from.

        Example:
            ```python
            images = await client.yahoo.media.images("cats")
            for img in images.results:
                print(img.image_url, img.source_url)
            ```
        """
        params: dict[str, Any] = {
            "query": query,
            "market": market,
            "count": count,
        }
        response = await self._client.get("/v1/yahoo/images", params=params)
        return ImagesResponse.model_validate(response)

    async def videos(
        self,
        query: str,
        *,
        market: str = "us",
        count: int = 30,
    ) -> VideosResponse:
        """Search Yahoo videos.

        Like images, Yahoo has no native page-size parameter here, so
        ``count`` trims the returned list.

        Args:
            query: Search keywords, e.g. ``"cats"``.
            market: Yahoo market code, e.g. ``"us"``.
            count: Number of videos to return (1-100).

        Returns:
            VideosResponse with video URLs, thumbnails, duration, host
            platform and view counts.

        Example:
            ```python
            videos = await client.yahoo.media.videos("cats")
            for v in videos.results:
                print(v.title, v.duration, v.views)
            ```
        """
        params: dict[str, Any] = {
            "query": query,
            "market": market,
            "count": count,
        }
        response = await self._client.get("/v1/yahoo/videos", params=params)
        return VideosResponse.model_validate(response)
