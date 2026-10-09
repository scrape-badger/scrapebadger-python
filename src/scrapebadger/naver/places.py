"""Naver Place API client.

Provides methods for place detail, reviews, and photos by place id.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.naver.models import (
    PlaceDetailResponse,
    PlacePhotosResponse,
    PlaceReviewsResponse,
)

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class PlacesClient:
    """Client for Naver Place endpoints (detail, reviews, photos).

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            place = await client.naver.places.get("1234567890")
            print(place.name, place.rating)

            reviews = await client.naver.places.reviews("1234567890")
            photos = await client.naver.places.photos("1234567890")
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize places client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def get(self, place_id: str) -> PlaceDetailResponse:
        """Get full place detail (business profile).

        Args:
            place_id: Naver Place id (digits, from ``search.local``).

        Returns:
            Place detail response including menus, hours, and images.
        """
        response = await self._client.get(f"/v1/naver/place/{place_id}")
        return PlaceDetailResponse.model_validate(response)

    async def reviews(
        self,
        place_id: str,
        *,
        cursor: str | None = None,
        size: int = 20,
    ) -> PlaceReviewsResponse:
        """Get paginated place reviews.

        Args:
            place_id: Naver Place id.
            cursor: Pagination cursor from a prior page.
            size: Reviews per page (1..50). Defaults to 20.

        Returns:
            Place reviews response with reviews and a next cursor.
        """
        params: dict[str, Any] = {"cursor": cursor, "size": size}
        response = await self._client.get(f"/v1/naver/place/{place_id}/reviews", params=params)
        return PlaceReviewsResponse.model_validate(response)

    async def photos(
        self,
        place_id: str,
        *,
        media_source: str = "placeReview",
        cursor: str | None = None,
    ) -> PlacePhotosResponse:
        """Get paginated place photos.

        Args:
            place_id: Naver Place id.
            media_source: Photo source ("placeReview" or "biz"). Defaults to "placeReview".
            cursor: Pagination cursor from a prior page.

        Returns:
            Place photos response with photos and a next cursor.
        """
        params: dict[str, Any] = {"media_source": media_source, "cursor": cursor}
        response = await self._client.get(f"/v1/naver/place/{place_id}/photos", params=params)
        return PlacePhotosResponse.model_validate(response)
