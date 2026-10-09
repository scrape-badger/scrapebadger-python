"""Naver Reviews API client.

Provides methods for commerce review detail, video playback keys, and SSR
query recipes under ``/v1/naver/reviews/*``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.naver.models import (
    ReviewDetailResponse,
    ReviewSsrQueriesResponse,
    ReviewVideoInkeyResponse,
)

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class ReviewsClient:
    """Client for Naver commerce review endpoints.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            detail = await client.naver.reviews.get("1234567890")
            inkey = await client.naver.reviews.video_inkey(
                attach_vid="abc", stamp="123",
            )
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize reviews client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def get(self, review_id: str) -> ReviewDetailResponse:
        """Get commerce review detail by id.

        Args:
            review_id: Review id.

        Returns:
            Review detail response.
        """
        response = await self._client.get(f"/v1/naver/reviews/{review_id}")
        return ReviewDetailResponse.model_validate(response)

    async def video_inkey(
        self,
        *,
        attach_vid: str,
        stamp: str,
    ) -> ReviewVideoInkeyResponse:
        """Get a video playback key minted from attachVid + videoStamp.

        Args:
            attach_vid: Attachment video id.
            stamp: Video stamp.

        Returns:
            Review video in-key response.
        """
        params: dict[str, Any] = {"attach_vid": attach_vid, "stamp": stamp}
        response = await self._client.get("/v1/naver/reviews/video-inkey", params=params)
        return ReviewVideoInkeyResponse.model_validate(response)

    async def ssr_queries(self, review_id: str) -> ReviewSsrQueriesResponse:
        """Get the SSR page query recipes for a review.

        Args:
            review_id: Review id.

        Returns:
            Review SSR queries response.
        """
        response = await self._client.get(f"/v1/naver/reviews/{review_id}/ssr-queries")
        return ReviewSsrQueriesResponse.model_validate(response)
