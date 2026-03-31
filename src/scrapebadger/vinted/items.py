"""Vinted Items API client.

Provides methods for fetching individual Vinted item details.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from scrapebadger.vinted.models import ItemDetailResponse

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class ItemsClient:
    """Client for Vinted item detail endpoints.

    Provides async methods for fetching detailed information about Vinted items.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            result = await client.vinted.items.get(123456789)
            item = result.item
            print(f"{item.title}: {item.description}")
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize items client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def get(
        self,
        item_id: int,
        *,
        market: str = "fr",
    ) -> ItemDetailResponse:
        """Get detailed information about a Vinted item.

        Args:
            item_id: The numeric item ID.
            market: Vinted market code (e.g. "fr", "de"). Defaults to "fr".

        Returns:
            Item detail response with full item data.

        Raises:
            NotFoundError: If the item doesn't exist.
            AuthenticationError: If the API key is invalid.

        Example:
            ```python
            result = await client.vinted.items.get(123456789, market="de")
            item = result.item
            print(f"{item.title}")
            print(f"Price: {item.price.amount} {item.price.currency_code}")
            print(f"Condition: {item.status}")
            print(f"Seller: {item.seller.login}")
            ```
        """
        response = await self._client.get(
            f"/v1/vinted/items/{item_id}",
            params={"market": market},
        )
        return ItemDetailResponse.model_validate(response)
