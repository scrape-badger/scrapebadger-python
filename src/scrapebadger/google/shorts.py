"""Google Shorts (short-form vertical videos) client."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class ShortsClient:
    """Client for Google Shorts search.

    Triggers Google's Shorts SERP mode via `udm=39` and returns the
    short_videos_results carousel — mostly YouTube Shorts but also
    TikToks, Facebook Reels, and other short-form sources when Google
    surfaces them.

    Example:
        ```python
        shorts = await client.google.shorts.search("cooking hacks")
        for video in shorts["short_videos_results"]:
            print(video["title"], video["source"], video["link"])
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
        num: int = 20,
        start: int = 0,
    ) -> dict[str, Any]:
        """Return short-form video results from Google Shorts mode.

        Args:
            q: Search query.
            gl: Country code.
            hl: Language code.
            domain: Google domain.
            num: Results per page (1-50).
            start: Pagination offset.

        Returns:
            Response with `search_information` and `short_videos_results[]` —
            each entry includes position, title, link, video_id (YouTube
            Shorts), thumbnail, source host, and channel/account metadata.
        """
        params: dict[str, Any] = {
            "q": q,
            "gl": gl,
            "hl": hl,
            "domain": domain,
            "num": num,
            "start": start,
        }
        return await self._client.get("/v1/google/shorts/search", params=params)
