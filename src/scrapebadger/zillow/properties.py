"""Zillow Properties API client.

Provides the method for fetching a single property's full detail.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from scrapebadger.zillow.models import Property, PropertyResponse

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class PropertiesClient:
    """Client for the Zillow property-detail endpoint.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            prop = await client.zillow.properties.get_property("2078133351")
            print(prop.street_address, prop.price)
            for event in prop.price_history:
                print(f"{event.date_at}: {event.event} {event.price}")
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize properties client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def get_property(self, zpid: str) -> Property:
        """Get a single Zillow property's full detail by its zpid.

        Args:
            zpid: The Zillow property id (zpid).

        Returns:
            Full property detail including price/valuation, specs, resoFacts
            (``home_facts``), price & tax history, schools, listing agent,
            mortgage rates, and photos.

        Raises:
            NotFoundError: If the property doesn't exist.
            AuthenticationError: If the API key is invalid.

        Example:
            ```python
            prop = await client.zillow.properties.get_property("2078133351")
            print(f"{prop.bedrooms}bd/{prop.bathrooms}ba, {prop.living_area} sqft")
            ```
        """
        response = await self._client.get(f"/v1/zillow/property/{zpid}")
        return PropertyResponse.model_validate(response).property
