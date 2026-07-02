"""Realtor Search API client.

Provides methods for property search and location autocomplete across the
supported real-estate markets (realtor.com US, realtor.ca CA).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.realtor.models import AutocompleteResponse, SearchResponse

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class SearchClient:
    """Client for Realtor search and autocomplete endpoints.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            results = await client.realtor.search.search("Austin, TX")
            for prop in results.results:
                print(prop.address.line if prop.address else prop.property_id)

            suggestions = await client.realtor.search.autocomplete("miami")
            for s in suggestions.suggestions:
                print(s.label)
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize search client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def search(
        self,
        location: str | None = None,
        *,
        market: str = "us",
        status: str = "for_sale",
        price_min: float | None = None,
        price_max: float | None = None,
        beds_min: int | None = None,
        baths_min: float | None = None,
        sqft_min: int | None = None,
        sqft_max: int | None = None,
        property_type: str | None = None,
        sort: str = "relevant",
        page: int = 1,
        limit: int | None = None,
        lat_min: float | None = None,
        lat_max: float | None = None,
        lng_min: float | None = None,
        lng_max: float | None = None,
    ) -> SearchResponse:
        """Search a real-estate market for property listings.

        Args:
            location: Freetext location ("Austin, TX", a ZIP, or "Toronto, ON").
                Required unless a CA bounding box (lat/lng) is supplied.
            market: Market — "us" (realtor.com, USD) or "ca" (realtor.ca, CAD).
                Defaults to "us".
            status: Listing status ("for_sale", "for_rent", "sold", "pending").
                Defaults to "for_sale".
            price_min: Minimum price filter.
            price_max: Maximum price filter.
            beds_min: Minimum number of bedrooms.
            baths_min: Minimum number of bathrooms.
            sqft_min: Minimum living area in sqft (US).
            sqft_max: Maximum living area in sqft (US).
            property_type: Property type filter (US, CSV: single_family, condos,
                townhomes, multi_family, mobile, land).
            sort: Sort order ("relevant", "newest", "price_low", "price_high",
                "photo_count"). Defaults to "relevant".
            page: Page number (1-indexed). Defaults to 1.
            limit: Results per page (1-200).
            lat_min: Bounding-box minimum latitude (CA power-user bbox).
            lat_max: Bounding-box maximum latitude (CA power-user bbox).
            lng_min: Bounding-box minimum longitude (CA power-user bbox).
            lng_max: Bounding-box maximum longitude (CA power-user bbox).

        Returns:
            Search response with matching property results and pagination metadata.

        Raises:
            AuthenticationError: If the API key is invalid.
            ValidationError: If the parameters are invalid.

        Example:
            ```python
            results = await client.realtor.search.search(
                "Austin, TX",
                price_min=300000,
                price_max=600000,
                beds_min=3,
                sort="newest",
            )
            print(f"Page {results.page} of {results.total_pages}")
            ```
        """
        params: dict[str, Any] = {
            "location": location,
            "market": market,
            "status": status,
            "price_min": price_min,
            "price_max": price_max,
            "beds_min": beds_min,
            "baths_min": baths_min,
            "sqft_min": sqft_min,
            "sqft_max": sqft_max,
            "property_type": property_type,
            "sort": sort,
            "page": page,
            "limit": limit,
            "lat_min": lat_min,
            "lat_max": lat_max,
            "lng_min": lng_min,
            "lng_max": lng_max,
        }
        response = await self._client.get("/v1/realtor/search", params=params)
        return SearchResponse.model_validate(response)

    async def autocomplete(
        self,
        query: str,
        *,
        market: str = "us",
        limit: int = 10,
    ) -> AutocompleteResponse:
        """Get location/address autocomplete suggestions.

        Args:
            query: Partial location or address query.
            market: Market — "us" or "ca". Defaults to "us".
            limit: Maximum suggestions to return (1-25). Defaults to 10.

        Returns:
            Autocomplete response with location/address suggestions.

        Example:
            ```python
            result = await client.realtor.search.autocomplete("austin")
            for s in result.suggestions:
                print(s.label)
            ```
        """
        params: dict[str, Any] = {"query": query, "market": market, "limit": limit}
        response = await self._client.get("/v1/realtor/autocomplete", params=params)
        return AutocompleteResponse.model_validate(response)
