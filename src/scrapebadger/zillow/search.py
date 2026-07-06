"""Zillow Search API client.

Provides methods for property search and region/address autocomplete on
zillow.com (for-sale / for-rent / recently-sold inventory).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.zillow.models import AutocompleteResponse, SearchResponse

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class SearchClient:
    """Client for Zillow search and autocomplete endpoints.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            results = await client.zillow.search.search("Austin, TX")
            for listing in results.results:
                print(listing.address, listing.price)

            hits = await client.zillow.search.autocomplete("austin")
            for r in hits.results:
                print(r.display, r.region_id)
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
        location: str,
        *,
        status: str = "for_sale",
        page: int = 1,
        sort: str | None = None,
        price_min: int | None = None,
        price_max: int | None = None,
        beds_min: int | None = None,
        baths_min: float | None = None,
        home_type: str | None = None,
        sqft_min: int | None = None,
        sqft_max: int | None = None,
        lot_min: int | None = None,
        lot_max: int | None = None,
        year_built_min: int | None = None,
        year_built_max: int | None = None,
        hoa_max: int | None = None,
        keywords: str | None = None,
        days_on: str | None = None,
        north: float | None = None,
        south: float | None = None,
        east: float | None = None,
        west: float | None = None,
    ) -> SearchResponse:
        """Search Zillow for property listings.

        Args:
            location: City/state, ZIP, address, or neighborhood ("Austin, TX").
            status: Listing status ("for_sale", "for_rent", "sold").
                Defaults to "for_sale".
            page: Page number (1-20; Zillow caps search at ~820 results).
                Defaults to 1.
            sort: Sort order ("homes_for_you", "newest", "price_high_to_low",
                "price_low_to_high", "bedrooms", "bathrooms", "square_feet",
                "lot_size", "year_built").
            price_min: Minimum price filter.
            price_max: Maximum price filter.
            beds_min: Minimum number of bedrooms (0-10).
            baths_min: Minimum number of bathrooms (0-10).
            home_type: Home type filter ("houses", "condos", "townhomes",
                "apartments", "manufactured", "lots", "multi_family").
            sqft_min: Minimum living area in sqft.
            sqft_max: Maximum living area in sqft.
            lot_min: Minimum lot size in sqft.
            lot_max: Maximum lot size in sqft.
            year_built_min: Minimum year built.
            year_built_max: Maximum year built.
            hoa_max: Maximum monthly HOA fee.
            keywords: Match listing description keywords.
            days_on: Days-on-Zillow filter (e.g. "1", "7", "30").
            north: Map-bounds north latitude (for tiling past the 820 cap).
            south: Map-bounds south latitude.
            east: Map-bounds east longitude.
            west: Map-bounds west longitude.

        Returns:
            Search response with matching listings, the resolved region, map
            bounds (for tiling), and pagination metadata.

        Raises:
            AuthenticationError: If the API key is invalid.
            ValidationError: If the parameters are invalid.

        Example:
            ```python
            results = await client.zillow.search.search(
                "Austin, TX",
                price_min=300000,
                price_max=600000,
                beds_min=3,
                sort="newest",
            )
            print(f"{results.map_results_count} homes on the map")
            ```
        """
        params: dict[str, Any] = {
            "location": location,
            "status": status,
            "page": page,
            "sort": sort,
            "price_min": price_min,
            "price_max": price_max,
            "beds_min": beds_min,
            "baths_min": baths_min,
            "home_type": home_type,
            "sqft_min": sqft_min,
            "sqft_max": sqft_max,
            "lot_min": lot_min,
            "lot_max": lot_max,
            "year_built_min": year_built_min,
            "year_built_max": year_built_max,
            "hoa_max": hoa_max,
            "keywords": keywords,
            "days_on": days_on,
            "north": north,
            "south": south,
            "east": east,
            "west": west,
        }
        response = await self._client.get("/v1/zillow/search", params=params)
        return SearchResponse.model_validate(response)

    async def autocomplete(self, query: str) -> AutocompleteResponse:
        """Resolve a search term to Zillow regions/addresses.

        Args:
            query: Partial location — city, ZIP, address, or neighborhood.

        Returns:
            Autocomplete response with region/address suggestions (each with a
            regionId and lat/lng; a zpid when the suggestion is a specific home).

        Example:
            ```python
            result = await client.zillow.search.autocomplete("austin")
            for r in result.results:
                print(r.display, r.region_type)
            ```
        """
        params: dict[str, Any] = {"query": query}
        response = await self._client.get("/v1/zillow/autocomplete", params=params)
        return AutocompleteResponse.model_validate(response)
