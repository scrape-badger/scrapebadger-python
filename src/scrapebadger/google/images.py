"""Google Images client."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class ImagesClient:
    """Client for Google Images search.

    Returns up to 100 tiles per page with ``title``, ``source``,
    ``link`` (referrer page), ``thumbnail``, ``image`` (inline
    preview), ``original`` (full-resolution URL), ``original_width`` /
    ``original_height``, ``original_size`` (e.g. ``"635KB"``), plus
    licensability flags (``is_product``, ``is_licensable``,
    ``is_video``).

    Example:
        ```python
        results = await client.google.images.search(
            "golden retriever", imgsz="l", imgcolor="color",
        )
        for img in results["results"]:
            print(img["rank"], img["title"], img["original"])
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
        page: int = 0,
        results: int = 100,
        safe: str = "off",
        tbs: str | None = None,
        imgsz: str | None = None,
        imgcolor: str | None = None,
        imgtype: str | None = None,
    ) -> dict[str, Any]:
        """Search Google Images.

        Args:
            q: Image search query.
            gl: Country code (ISO 3166 alpha-2).
            hl: Language code.
            page: Zero-based page index (each page ≈ 100 tiles).
            results: Max tiles to return (1-500, client-side cap).
            safe: Safe search ``"off"`` or ``"active"``.
            tbs: Raw Google tbs filter (e.g. ``"qdr:d"`` for past 24h).
            imgsz: Size filter: ``"l"`` large, ``"m"`` medium, ``"i"``
                icon, ``"xXl"`` / ``"xxl"`` / ``"xxxl"`` extra-large.
            imgcolor: Colour filter (``"color"``, ``"gray"``,
                ``"transparent"``, ``"red"``, ``"orange"``, …).
            imgtype: ``"face"``, ``"photo"``, ``"clipart"``,
                ``"lineart"``, ``"animated"``.
        """
        params: dict[str, Any] = {
            "q": q,
            "gl": gl,
            "hl": hl,
            "safe": safe,
            "page": page,
            "results": results,
        }
        if tbs:
            params["tbs"] = tbs
        if imgsz:
            params["imgsz"] = imgsz
        if imgcolor:
            params["imgcolor"] = imgcolor
        if imgtype:
            params["imgtype"] = imgtype
        return await self._client.get("/v1/google/images/search", params=params)
