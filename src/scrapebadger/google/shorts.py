"""Google Shorts (short-form vertical videos) client."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class ShortsClient:
    """Client for Google Shorts search (``udm=39``).

    Returns a carousel of short-form videos Google surfaces for a
    query — YouTube Shorts plus TikToks, Instagram Reels, Facebook
    Reels, and other platforms. Every tile carries ``title``,
    ``link``, ``source`` (platform label — ``"YouTube"`` /
    ``"TikTok"`` / …), ``account_name``, ``thumbnail``, ``image``
    (inline preview), ``duration``, and ``video_id`` (YouTube only).

    Example:
        ```python
        shorts = await client.google.shorts.search("cooking hacks")
        for v in shorts["short_videos_results"]:
            print(v["rank"], v["title"], v["source"], v["account_name"])
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
        domain: str = "google.com",
        num: int = 40,
        start: int = 0,
        safe: str = "off",
        nfpr: int = 0,
        tbs: str | None = None,
    ) -> dict[str, Any]:
        """Return short-form video results from Google's Shorts carousel.

        Args:
            q: Search query.
            gl: Country code.
            hl: Language code.
            domain: Google domain (``"google.com"`` / ``"google.co.uk"`` / …).
            num: Max tiles to return (1-60).
            start: Pagination offset.
            safe: ``"off"`` or ``"active"``.
            nfpr: ``1`` disables auto-correction.
            tbs: Raw Google ``tbs`` filter (e.g. ``"qdr:d"``).
        """
        params: dict[str, Any] = {
            "q": q,
            "gl": gl,
            "hl": hl,
            "domain": domain,
            "num": num,
            "start": start,
            "safe": safe,
        }
        if nfpr:
            params["nfpr"] = nfpr
        if tbs:
            params["tbs"] = tbs
        return await self._client.get("/v1/google/shorts/search", params=params)
