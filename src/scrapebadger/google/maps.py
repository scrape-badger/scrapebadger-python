"""Google Maps client — place search, details, reviews, photos, posts."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class MapsClient:
    """Client for Google Maps endpoints.

    Example:
        ```python
        # Search for places
        places = await client.google.maps.search("coffee shops in sf")
        for p in places["results"]:
            print(p["title"], p["rating"])

        # Get place details
        detail = await client.google.maps.place(data_id="0x80859a6b:0x12345")

        # Get reviews
        reviews = await client.google.maps.reviews(
            data_id="0x80859a6b:0x12345",
            sort_by="newestFirst",
        )
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        self._client = client

    async def search(
        self,
        q: str,
        *,
        ll: str | None = None,
        gl: str = "us",
        hl: str = "en",
        start: int = 0,
    ) -> dict[str, Any]:
        """Search Google Maps for places.

        Args:
            q: Search query (e.g. "pizza in New York").
            ll: GPS coordinates in the form "@lat,lng,zoom".
            gl: Country code.
            hl: Language code.
            start: Pagination offset (increments of 20).
        """
        params: dict[str, Any] = {"q": q, "gl": gl, "hl": hl, "start": start}
        if ll is not None:
            params["ll"] = ll
        return await self._client.get("/v1/google/maps/search", params=params)

    async def place(
        self,
        *,
        place_id: str | None = None,
        data_id: str | None = None,
        hl: str = "en",
        gl: str = "us",
    ) -> dict[str, Any]:
        """Get place details by `place_id` or `data_id`.

        At least one of `place_id` or `data_id` must be provided.
        """
        if not place_id and not data_id:
            raise ValueError("Either place_id or data_id is required")
        params: dict[str, Any] = {"hl": hl, "gl": gl}
        if place_id:
            params["place_id"] = place_id
        if data_id:
            params["data_id"] = data_id
        return await self._client.get("/v1/google/maps/place", params=params)

    async def reviews(
        self,
        data_id: str,
        *,
        sort_by: str = "qualityScore",
        hl: str = "en",
        next_page_token: str | None = None,
        results: int = 10,
    ) -> dict[str, Any]:
        """Get reviews for a place.

        Args:
            data_id: Google Maps location ID.
            sort_by: One of "qualityScore", "newestFirst", "ratingHigh", "ratingLow".
            hl: Language code.
            next_page_token: Pagination token from a previous response.
            results: Reviews per page (1-20).
        """
        params: dict[str, Any] = {
            "data_id": data_id,
            "sort_by": sort_by,
            "hl": hl,
            "results": results,
        }
        if next_page_token:
            params["next_page_token"] = next_page_token
        return await self._client.get("/v1/google/maps/reviews", params=params)

    async def photos(
        self,
        data_id: str,
        *,
        hl: str = "en",
        next_page_token: str | None = None,
    ) -> dict[str, Any]:
        """Get photos for a place."""
        params: dict[str, Any] = {"data_id": data_id, "hl": hl}
        if next_page_token:
            params["next_page_token"] = next_page_token
        return await self._client.get("/v1/google/maps/photos", params=params)

    async def posts(
        self,
        data_id: str,
        *,
        next_page_token: str | None = None,
    ) -> dict[str, Any]:
        """Get business posts for a place."""
        params: dict[str, Any] = {"data_id": data_id}
        if next_page_token:
            params["next_page_token"] = next_page_token
        return await self._client.get("/v1/google/maps/posts", params=params)
