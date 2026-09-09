"""Zillow Properties API client.

Provides the method for fetching a single property's full detail.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from scrapebadger.zillow.models import Building, BuildingResponse, Property, PropertyResponse

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class PropertiesClient:
    """Client for the Zillow property- and building-detail endpoints.

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

    async def get_building(self, url: str) -> Building:
        """Get a Zillow multifamily building (apartment community) by its URL.

        Zillow serves multi-unit rentals on ``/apartments/...`` and ``/b/...``
        pages, which :meth:`get_property` cannot read. Pass the ``detail_url``
        of a search result whose ``home_type`` is ``"BUILDING"``.

        Args:
            url: Full Zillow building URL, e.g.
                ``https://www.zillow.com/apartments/kansas-city-mo/brookside-51/CkBJqt/``.

        Returns:
            The building with its floor plans and every available unit
            (rent, base rent, required monthly fees, sqft, beds/baths, move-in
            date), plus amenities, office hours, pet policy, schools, photos
            and walk/transit/bike scores.

        Raises:
            NotFoundError: If the building doesn't exist.
            AuthenticationError: If the API key is invalid.

        Example:
            ```python
            b = await client.zillow.properties.get_building(
                "https://www.zillow.com/apartments/kansas-city-mo/brookside-51/CkBJqt/"
            )
            for unit in b.units:
                print(unit.unit_number, unit.beds, unit.sqft, unit.price)
            ```
        """
        response = await self._client.get("/v1/zillow/building", params={"url": url})
        return BuildingResponse.model_validate(response).building
