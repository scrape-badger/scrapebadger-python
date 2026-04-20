"""Google Videos client."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class VideosClient:
    """Client for Google Videos search (``udm=7`` vertical).

    Returns up to 10 tiles per page with ``title``, ``link``
    (YouTube / Vimeo / etc.), ``displayed_link``, ``snippet``,
    ``thumbnail``, ``image`` (inline base-64), ``favicon``,
    ``duration``, ``channel``, ``source`` (platform label),
    ``date``, ``video_id``, and the raw ``extensions`` chip list.

    Example:
        ```python
        videos = await client.google.videos.search("python tutorial")
        for v in videos["results"]:
            print(v["rank"], v["title"], v["duration"], v["channel"])
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
        domain: str = "google.com",
        location: str | None = None,
        lr: str | None = None,
        uule: str | None = None,
        nfpr: int = 0,
        safe: str = "off",
        tbs: str | None = None,
    ) -> dict[str, Any]:
        """Search Google for video results.

        Args:
            q: Video search query.
            gl: Country code.
            hl: Language code.
            page: Zero-based page index (each page ≈ 10 tiles).
            domain: Google domain (``"google.com"`` / ``"google.co.uk"`` / …).
            location: City-level geo-targeting.
            lr: Language restrict (``"lang_en"`` …).
            uule: UULE-encoded location.
            nfpr: ``1`` disables auto-correction.
            safe: ``"off"`` or ``"active"``.
            tbs: Time/duration chip (e.g. ``"qdr:w"`` past week,
                ``"dur:s"`` short videos).
        """
        params: dict[str, Any] = {
            "q": q,
            "gl": gl,
            "hl": hl,
            "safe": safe,
            "page": page,
            "domain": domain,
        }
        if location:
            params["location"] = location
        if lr:
            params["lr"] = lr
        if uule:
            params["uule"] = uule
        if nfpr:
            params["nfpr"] = nfpr
        if tbs:
            params["tbs"] = tbs
        return await self._client.get("/v1/google/videos/search", params=params)
