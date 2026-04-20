"""Google Maps client — place search, details, reviews, photos, posts."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class MapsClient:
    """Client for Google Maps endpoints.

    Example:
        ```python
        # Search for places (Maxima stores in Lithuania)
        places = await client.google.maps.search("maxima", gl="lt")
        for p in places["results"]:
            print(p["title"], p["rating"], p["address"])

        # Direct place lookup by Google Place ID (ChIJ...)
        place = await client.google.maps.search(place_id="ChIJ_3Su08fj5UYRkFfNoiuWQUk")

        # Full place detail with rating breakdown + popular times
        detail = await client.google.maps.place(
            place_id="ChIJ_3Su08fj5UYRkFfNoiuWQUk"
        )
        print(detail["place"]["rating_summary"])

        # Reviews with topic filter
        reviews = await client.google.maps.reviews(
            data_id="0x46e5e3c7d3ae74ff:0x4941962ba2cd5790",
            sort_by="newestFirst",
        )
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        self._client = client

    async def search(
        self,
        q: str | None = None,
        *,
        ll: str | None = None,
        gl: str = "us",
        hl: str = "en",
        start: int = 0,
        page: int | None = None,
        type: str | None = None,
        data: str | None = None,
        place_id: str | None = None,
        ludocid: str | None = None,
    ) -> dict[str, Any]:
        """Search Google Maps for places.

        Returns up to 20 results per page with full details (place_id,
        data_id, GPS, rating, reviews, address, phone, website, extensions,
        weekly hours, thumbnail) in a single call.

        Args:
            q: Search query (e.g. "pizza in New York"). Required unless
                ``place_id`` or ``ludocid`` is provided.
            ll: GPS coords ``@lat,lng,zoom`` (e.g. ``@40.745,-74.008,14z``).
                Defaults to the country capital at city zoom.
            gl: Country code (e.g. ``us``, ``lt``, ``de``).
            hl: Language code.
            start: Pagination offset (increments of 20).
            page: 1-indexed page number (alternative to ``start``).
            type: Business-type slug (e.g. ``restaurant``, ``hotel``,
                ``coffee_shop``) — filters by Google's category.
            data: Raw Google Maps ``pb=`` parameter override for
                advanced queries; replaces the auto-built viewport.
            place_id: Google Place ID (``ChIJ...``) — direct-lookup
                a single place. Returns a one-item ``results`` list.
            ludocid: Google Location Document ID (CID) — direct-lookup
                a single place by CID.
        """
        params: dict[str, Any] = {"gl": gl, "hl": hl, "start": start}
        if q is not None:
            params["q"] = q
        if ll is not None:
            params["ll"] = ll
        if page is not None:
            params["page"] = page
        if type is not None:
            params["type"] = type
        if data is not None:
            params["data"] = data
        if place_id is not None:
            params["place_id"] = place_id
        if ludocid is not None:
            params["ludocid"] = ludocid
        return await self._client.get("/v1/google/maps/search", params=params)

    async def place(
        self,
        *,
        place_id: str | None = None,
        data_id: str | None = None,
        hl: str = "en",
        gl: str = "us",
    ) -> dict[str, Any]:
        """Get full place detail by ``place_id`` or ``data_id``.

        Returns title, address, phone, website, GPS, rating, reviews_count,
        rating_summary (per-star distribution), categories, extensions
        (service_options, accessibility, offerings, payments, etc.),
        weekly operating hours, popular_times graph (per-weekday busyness),
        provider_id, permanently_closed flag, thumbnail, and photo list.

        At least one of ``place_id`` or ``data_id`` must be provided.
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
        sort_by: Literal["qualityScore", "newestFirst", "ratingHigh", "ratingLow"] = "qualityScore",
        hl: str = "en",
        gl: str = "us",
        next_page_token: str | None = None,
        offset: int = 0,
        results: int = 10,
        topic_id: str | None = None,
    ) -> dict[str, Any]:
        """Get reviews for a place.

        Args:
            data_id: Google Maps data ID (``0x...:0x...``).
            sort_by: Sort order. One of ``qualityScore`` (Most Relevant),
                ``newestFirst``, ``ratingHigh``, or ``ratingLow``. Note:
                Google currently ignores this field on the public reviews
                endpoint — all four return the same set.
            hl: Language code.
            gl: Country code.
            next_page_token: Pagination token from previous
                ``response.pagination.next``.
            offset: Review offset (alternative to ``next_page_token``).
            results: Reviews per page (1-20).
            topic_id: Filter to reviews tagged with this topic ID
                (from ``response.topics[].id``).
        """
        params: dict[str, Any] = {
            "data_id": data_id,
            "sort_by": sort_by,
            "hl": hl,
            "gl": gl,
            "offset": offset,
            "results": results,
        }
        if next_page_token:
            params["next_page_token"] = next_page_token
        if topic_id:
            params["topic_id"] = topic_id
        return await self._client.get("/v1/google/maps/reviews", params=params)

    async def photos(
        self,
        data_id: str,
        *,
        hl: str = "en",
        gl: str = "us",
        category_id: str | None = None,
        next_page_token: str | None = None,
        page_size: int = 20,
    ) -> dict[str, Any]:
        """Get photos for a place.

        Returns place-specific photo categories (Menu, Vibe, Comfort food,
        individual dish names, etc.), photo URLs from all CDN families
        (``/p/AF1Qip*``, ``/gps-cs-s/*``, ``/gps-proxy/*``), the total
        photo count, and a pagination token.

        Args:
            data_id: Google Maps data ID (``0x...:0x...``).
            hl: Language code.
            gl: Country code.
            category_id: Filter by category ID from
                ``response.categories[].id`` (e.g. Menu, Vibe).
            next_page_token: Pagination token from previous
                ``response.pagination.next``.
            page_size: Photos per page (1-200). Use 200 to fetch all
                photos in a single call for places with <~120 photos.
        """
        params: dict[str, Any] = {"data_id": data_id, "hl": hl, "gl": gl, "page_size": page_size}
        if category_id:
            params["category_id"] = category_id
        if next_page_token:
            params["next_page_token"] = next_page_token
        return await self._client.get("/v1/google/maps/photos", params=params)

    async def posts(
        self,
        data_id: str | None = None,
        *,
        place_id: str | None = None,
        hl: str = "en",
        gl: str = "us",
        next_page_token: str | None = None,
    ) -> dict[str, Any]:
        """Get business posts (promotional updates, announcements) for a place.

        Either ``data_id`` or ``place_id`` must be supplied.

        Args:
            data_id: Hex-format place identifier.
            place_id: Alternative place identifier from Maps search.
            hl: Language code.
            gl: Country code.
            next_page_token: Pagination token from a previous response.
        """
        if not data_id and not place_id:
            raise ValueError("Either data_id or place_id is required")
        params: dict[str, Any] = {"hl": hl, "gl": gl}
        if data_id:
            params["data_id"] = data_id
        if place_id:
            params["place_id"] = place_id
        if next_page_token:
            params["next_page_token"] = next_page_token
        return await self._client.get("/v1/google/maps/posts", params=params)
