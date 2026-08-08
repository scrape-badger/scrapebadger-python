"""Yandex Image Search API client (forward search + reverse / CBIR)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.yandex.models import ImagesResponse, ReverseImageResponse

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class ImagesClient:
    """Client for the Yandex image search and reverse-image endpoints.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            images = await client.yandex.images.search("golden retriever")
            reverse = await client.yandex.images.reverse(
                "https://example.com/photo.jpg"
            )
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize images client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def search(
        self,
        query: str,
        *,
        domain: str = "tr",
        page: int = 1,
    ) -> ImagesResponse:
        """Search Yandex images.

        Args:
            query: Search keywords, e.g. ``"golden retriever"``.
            domain: Market domain — ``"tr"`` (default), ``"com"``, ``"ru"``,
                ``"by"``, ``"kz"``, ``"uz"``.
            page: Page number (1-25).

        Returns:
            ImagesResponse with the image results and suggested searches.

        Example:
            ```python
            result = await client.yandex.images.search("sunset")
            for img in result.results:
                print(img.image.url if img.image else None, img.source)
            ```
        """
        params: dict[str, Any] = {
            "query": query,
            "domain": domain,
            "page": page,
        }
        response = await self._client.get("/v1/yandex/images/search", params=params)
        return ImagesResponse.model_validate(response)

    async def reverse(
        self,
        image_url: str,
        *,
        domain: str = "tr",
    ) -> ReverseImageResponse:
        """Reverse-image (CBIR) search for a given image URL.

        Args:
            image_url: The publicly reachable URL of the query image.
            domain: Market domain — ``"tr"`` (default), ``"com"``, ``"ru"``,
                ``"by"``, ``"kz"``, ``"uz"``.

        Returns:
            ReverseImageResponse with matching sites, similar images, tags, and
            the same image at other sizes.

        Example:
            ```python
            result = await client.yandex.images.reverse(
                "https://example.com/photo.jpg"
            )
            for site in result.sites:
                print(site.title, site.url)
            ```
        """
        params: dict[str, Any] = {
            "image_url": image_url,
            "domain": domain,
        }
        response = await self._client.get("/v1/yandex/images/reverse", params=params)
        return ReverseImageResponse.model_validate(response)
