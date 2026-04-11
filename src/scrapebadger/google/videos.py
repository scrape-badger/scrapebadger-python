"""Google Videos client."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class VideosClient:
    """Client for Google Videos search.

    Example:
        ```python
        videos = await client.google.videos.search("python tutorial")
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        self._client = client

    async def search(
        self,
        q: str,
        *,
        gl: str = "us",
        hl: str = "en",
        tbs: str | None = None,
        safe: str = "off",
        page: int = 0,
    ) -> dict[str, Any]:
        """Search Google for video results.

        Args:
            q: Video search query.
            gl: Country code.
            hl: Language code.
            tbs: Time filter (e.g. "qdr:w" past week).
            safe: Safe search toggle.
            page: Page number.
        """
        params: dict[str, Any] = {"q": q, "gl": gl, "hl": hl, "safe": safe, "page": page}
        if tbs:
            params["tbs"] = tbs
        return await self._client.get("/v1/google/videos/search", params=params)
