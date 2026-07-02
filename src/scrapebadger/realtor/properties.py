"""Realtor Properties API client.

Provides the method for fetching a single property's full detail.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.realtor.models import PropertyDetail

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class PropertiesClient:
    """Client for the Realtor property-detail endpoint.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            detail = await client.realtor.properties.get_property("1234567890")
            print(detail.address.line if detail.address else detail.property_id)
            for event in detail.price_history:
                print(f"{event.date_at}: {event.event} {event.price}")
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize properties client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def get_property(
        self,
        property_id: str,
        *,
        market: str = "us",
    ) -> PropertyDetail:
        """Get a single property's full detail.

        Args:
            property_id: The property id.
            market: Market — "us" or "ca". Defaults to "us".

        Returns:
            Full property detail including price/tax history, schools, estimates,
            amenities, and agent/office contacts.

        Raises:
            NotFoundError: If the property doesn't exist.
            AuthenticationError: If the API key is invalid.

        Example:
            ```python
            detail = await client.realtor.properties.get_property("1234567890")
            print(f"{detail.beds}bd/{detail.baths}ba, {detail.sqft} sqft")
            ```
        """
        params: dict[str, Any] = {"market": market}
        response = await self._client.get(f"/v1/realtor/properties/{property_id}", params=params)
        return PropertyDetail.model_validate(response)
