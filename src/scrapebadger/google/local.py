"""Google Local (Local Pack) client."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class LocalClient:
    """Client for Google Local Pack search.

    Distinct from the Maps API: driven by a query + location/uule rather
    than a place_id, and ordered the way Google ranks local results in
    the main SERP (via `tbm=lcl`). Use it for local-SEO research, rank
    tracking, and building directory datasets without going through the
    Maps Protobuf API.

    Example:
        ```python
        local = await client.google.local.search(
            "coffee shops in brooklyn",
            uule="w+CAIQICIRQnJvb2tseW4sIE5ZLCBVU0E",
        )
        for place in local["local_results"]:
            print(place["title"], place["rating"], place["phone"])
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
        location: str | None = None,
        uule: str | None = None,
        num: int = 20,
        start: int = 0,
    ) -> dict[str, Any]:
        """Return Google Local Pack business listings ranked for a SERP query.

        Args:
            q: Search query with local intent (e.g. "pizza in brooklyn").
            gl: Country code.
            hl: Language code.
            domain: Google domain (e.g. "google.co.uk").
            location: City-level geo-targeting string (e.g. "New York, USA").
            uule: UULE-encoded location parameter.
            num: Results per page (1-100).
            start: Pagination offset.

        Returns:
            Response with `search_information` and `local_results[]` —
            each entry includes title, place_id, rating, reviews, address,
            phone, type, and gps_coordinates when available.
        """
        params: dict[str, Any] = {
            "q": q,
            "gl": gl,
            "hl": hl,
            "domain": domain,
            "num": num,
            "start": start,
        }
        if location is not None:
            params["location"] = location
        if uule is not None:
            params["uule"] = uule
        return await self._client.get("/v1/google/local/search", params=params)
