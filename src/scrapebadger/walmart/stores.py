"""Walmart Stores API client.

Physical store detail — address, geo, hours, per-department services, and the
stores nearby.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from scrapebadger.walmart.models import StoreResponse

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class StoresClient:
    """Client for the Walmart store endpoint.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            result = await client.walmart.stores.get_store("100")
            print(result.store.city, result.store.phone)
            for svc in result.store.services:
                print(svc.display_name, svc.phone)
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize stores client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def get_store(self, store_id: str) -> StoreResponse:
        """Get a store's detail plus every store around it.

        Args:
            store_id: Walmart store number, e.g. ``"100"``.

        Returns:
            StoreResponse with the store's address, geo, phone, opening hours
            and per-department services (each with its own hours and phone),
            plus ~30 nearby stores with the same shape.

        Raises:
            NotFoundError: If the store doesn't exist.

        Example:
            ```python
            result = await client.walmart.stores.get_store("100")
            print(f"{result.nearby_count} stores nearby")
            ```
        """
        response = await self._client.get(f"/v1/walmart/stores/{store_id}")
        return StoreResponse.model_validate(response)
