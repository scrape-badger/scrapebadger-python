"""Naver Shopping Live API client.

Provides methods for live-commerce search keywords, broadcasts, channels,
and shortclips under ``/v1/naver/shopping/live/*``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.naver.models import (
    LiveBroadcastCategoriesResponse,
    LiveBroadcastCountsResponse,
    LiveBroadcastDetailResponse,
    LiveBroadcastProductsResponse,
    LiveChannelBroadcastsResponse,
    LiveChannelProductsResponse,
    LiveChannelProfileResponse,
    LiveChannelShortclipsResponse,
    LiveReplayProductsResponse,
    LiveSearchKeywordsResponse,
    LiveShortclipDetailResponse,
    LiveShortclipProductsResponse,
)

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class LiveClient:
    """Client for Naver Shopping Live endpoints.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            live = client.naver.shopping.live
            detail = await live.broadcast("1234567")
            products = await live.broadcast_products("1234567")
            channel = await live.channel("abcdef")
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize Shopping Live client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def search_keywords(self) -> LiveSearchKeywordsResponse:
        """Get the Shopping Live search standby keyword ranking.

        Returns:
            Live search keywords response.
        """
        response = await self._client.get("/v1/naver/shopping/live/search/keywords")
        return LiveSearchKeywordsResponse.model_validate(response)

    async def broadcast(self, broadcast_id: str) -> LiveBroadcastDetailResponse:
        """Get broadcast detail including embedded shopping products.

        Args:
            broadcast_id: Broadcast id.

        Returns:
            Live broadcast detail response.
        """
        response = await self._client.get(f"/v1/naver/shopping/live/broadcasts/{broadcast_id}")
        return LiveBroadcastDetailResponse.model_validate(response)

    async def broadcast_products(
        self,
        broadcast_id: str,
        *,
        page: int | None = None,
        size: int | None = None,
    ) -> LiveBroadcastProductsResponse:
        """Get the paginated product list for one broadcast.

        Args:
            broadcast_id: Broadcast id.
            page: 0-based page; omit for the first page (page=1 returns an empty list).
            size: Products per page (1..200); omit for the upstream default.

        Returns:
            Live broadcast products response.
        """
        params: dict[str, Any] = {"page": page, "size": size}
        response = await self._client.get(
            f"/v1/naver/shopping/live/broadcasts/{broadcast_id}/products", params=params
        )
        return LiveBroadcastProductsResponse.model_validate(response)

    async def broadcast_counts(self, broadcast_id: str) -> LiveBroadcastCountsResponse:
        """Get a broadcast's viewer / like / comment counts.

        Args:
            broadcast_id: Broadcast id.

        Returns:
            Live broadcast counts response.
        """
        response = await self._client.get(
            f"/v1/naver/shopping/live/broadcasts/{broadcast_id}/counts"
        )
        return LiveBroadcastCountsResponse.model_validate(response)

    async def replay_products(
        self,
        broadcast_id: str,
        *,
        include_before: bool = True,
        next: str = "0",
    ) -> LiveReplayProductsResponse:
        """Get the replay product timeline of an ended broadcast.

        Args:
            broadcast_id: Broadcast id.
            include_before: Include pre-start products. Defaults to True.
            next: Pagination cursor ("0" = from the beginning). Defaults to "0".

        Returns:
            Live replay products response.
        """
        params: dict[str, Any] = {"include_before": include_before, "next": next}
        response = await self._client.get(
            f"/v1/naver/shopping/live/broadcasts/{broadcast_id}/replay-products", params=params
        )
        return LiveReplayProductsResponse.model_validate(response)

    async def broadcast_product_categories(
        self,
        broadcast_id: str,
        *,
        attachment_type: str | None = None,
    ) -> LiveBroadcastCategoriesResponse:
        """Get the product categories present in a broadcast.

        Args:
            broadcast_id: Broadcast id.
            attachment_type: Restrict to "MAIN" or "SUB" attachments.

        Returns:
            Live broadcast categories response.
        """
        params: dict[str, Any] = {"attachment_type": attachment_type}
        response = await self._client.get(
            f"/v1/naver/shopping/live/broadcasts/{broadcast_id}/product-categories", params=params
        )
        return LiveBroadcastCategoriesResponse.model_validate(response)

    async def channel(self, channel_id: str) -> LiveChannelProfileResponse:
        """Get a Shopping Live channel / store profile.

        Args:
            channel_id: Channel id.

        Returns:
            Live channel profile response.
        """
        response = await self._client.get(f"/v1/naver/shopping/live/channels/{channel_id}")
        return LiveChannelProfileResponse.model_validate(response)

    async def channel_products(
        self,
        channel_id: str,
        *,
        next: str | None = None,
        size: int | None = None,
    ) -> LiveChannelProductsResponse:
        """Get a channel's product list.

        Args:
            channel_id: Channel id.
            next: Pagination cursor from a prior page.
            size: Products per page (1..100); omit for the upstream default (10).

        Returns:
            Live channel products response.
        """
        params: dict[str, Any] = {"next": next, "size": size}
        response = await self._client.get(
            f"/v1/naver/shopping/live/channels/{channel_id}/products", params=params
        )
        return LiveChannelProductsResponse.model_validate(response)

    async def channel_broadcasts(self, channel_id: str) -> LiveChannelBroadcastsResponse:
        """Get a channel's broadcast list (including STANDBY schedule cards).

        Args:
            channel_id: Channel id.

        Returns:
            Live channel broadcasts response.
        """
        response = await self._client.get(
            f"/v1/naver/shopping/live/channels/{channel_id}/broadcasts"
        )
        return LiveChannelBroadcastsResponse.model_validate(response)

    async def channel_shortclips(
        self,
        channel_id: str,
        *,
        sort_type: str | None = None,
        next: str | None = None,
        size: int | None = None,
    ) -> LiveChannelShortclipsResponse:
        """Get a channel's shorts / clips list.

        Args:
            channel_id: Channel id.
            sort_type: Sort order ("LATEST", "VIEW", or "RECOMMEND").
            next: Pagination cursor from a prior page.
            size: Clips per page (1..100); omit for the upstream default (10).

        Returns:
            Live channel shortclips response.
        """
        params: dict[str, Any] = {"sort_type": sort_type, "next": next, "size": size}
        response = await self._client.get(
            f"/v1/naver/shopping/live/channels/{channel_id}/shortclips", params=params
        )
        return LiveChannelShortclipsResponse.model_validate(response)

    async def shortclip(self, shortclip_id: str) -> LiveShortclipDetailResponse:
        """Get shortclip detail with embedded products and categories.

        Args:
            shortclip_id: Shortclip id.

        Returns:
            Live shortclip detail response.
        """
        response = await self._client.get(f"/v1/naver/shopping/live/shortclips/{shortclip_id}")
        return LiveShortclipDetailResponse.model_validate(response)

    async def shortclip_products(
        self,
        shortclip_id: str,
        *,
        attachment_type: str | None = None,
        page: int | None = None,
        size: int | None = None,
        sort: str | None = None,
    ) -> LiveShortclipProductsResponse:
        """Get the paginated product list for one shortclip.

        Args:
            shortclip_id: Shortclip id.
            attachment_type: Restrict to "MAIN" or "SUB" attachments.
            page: 0-based page.
            size: Products per page (1..100).
            sort: Sort order ("RECOMMEND" or "POPULAR").

        Returns:
            Live shortclip products response.
        """
        params: dict[str, Any] = {
            "attachment_type": attachment_type,
            "page": page,
            "size": size,
            "sort": sort,
        }
        response = await self._client.get(
            f"/v1/naver/shopping/live/shortclips/{shortclip_id}/products", params=params
        )
        return LiveShortclipProductsResponse.model_validate(response)
