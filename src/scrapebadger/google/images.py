"""Google Images client."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class ImagesClient:
    """Client for Google Images search.

    Example:
        ```python
        results = await client.google.images.search(
            "golden retriever",
            imgsz="l",
            imgcolor="color",
        )
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
        imgsz: str | None = None,
        imgcolor: str | None = None,
        imgtype: str | None = None,
        safe: str = "off",
        page: int = 0,
    ) -> dict[str, Any]:
        """Search Google Images.

        Args:
            q: Image search query.
            gl: Country code.
            hl: Language code.
            tbs: Time/filter string (e.g. "qdr:d" past day).
            imgsz: Image size filter: "l" (large), "m" (medium), "i" (icon), "xXl" (extra large).
            imgcolor: Image color filter (e.g. "color", "gray", "trans").
            imgtype: "face", "photo", "clipart", "lineart", "animated".
            safe: Safe search ("off", "medium", "high").
            page: Page number.
        """
        params: dict[str, Any] = {"q": q, "gl": gl, "hl": hl, "safe": safe, "page": page}
        if tbs:
            params["tbs"] = tbs
        if imgsz:
            params["imgsz"] = imgsz
        if imgcolor:
            params["imgcolor"] = imgcolor
        if imgtype:
            params["imgtype"] = imgtype
        return await self._client.get("/v1/google/images/search", params=params)
