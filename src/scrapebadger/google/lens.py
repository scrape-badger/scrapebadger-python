"""Google Lens client (visual image search)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class LensClient:
    """Client for Google Lens visual search by image URL.

    Example:
        ```python
        results = await client.google.lens.search(
            url="https://example.com/photo.jpg",
        )
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        self._client = client

    async def search(
        self,
        url: str,
        *,
        gl: str = "us",
        hl: str = "en",
    ) -> dict[str, Any]:
        """Search Google Lens with a public image URL.

        Args:
            url: Public URL of the image to search visually.
            gl: Country code.
            hl: Language code.
        """
        params: dict[str, Any] = {"url": url, "gl": gl, "hl": hl}
        return await self._client.get("/v1/google/lens/search", params=params)
