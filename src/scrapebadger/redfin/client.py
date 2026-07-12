"""Redfin API client.

Redfin endpoints: search (for-sale listings), get_property (full single-listing
detail, by property_id or URL), get_agent (agent profile + listings, by
agent_id or URL), autocomplete (location suggestions), and list_markets.
All methods are async and return strongly-typed Pydantic models. Single
market: redfin.com (US, USD, en-US).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.redfin.models import (
    AgentResponse,
    AutocompleteResponse,
    MarketsResponse,
    PropertyResponse,
    SearchResponse,
)

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class RedfinClient:
    """Client for all Redfin API operations.

    Example:
        ```python
        from scrapebadger import ScrapeBadger

        async with ScrapeBadger(api_key="your-key") as client:
            # Search for-sale listings
            results = await client.redfin.search("Austin, TX")
            for listing in results.results:
                print(f"{listing.position}. {listing.street_line} — {listing.price}")

            # Full single-listing detail
            detail = await client.redfin.get_property("12345678")
            print(detail.property.price)

            # Agent profile
            agent = await client.redfin.get_agent("jane-doe")

            # Supported markets
            markets = await client.redfin.list_markets()
        ```

    Note:
        This client is not instantiated directly. Instead, access it through
        the `redfin` property of the main `ScrapeBadger` client.
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize Redfin client.

        Args:
            client: The base HTTP client for making API requests.
        """
        self._client = client

    async def search(
        self,
        location: str,
        *,
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
        max_days_on_market: int | None = None,
        north: float | None = None,
        south: float | None = None,
        east: float | None = None,
        west: float | None = None,
    ) -> SearchResponse:
        """Search Redfin for for-sale properties.

        Args:
            location: City/state, ZIP, address or neighborhood (required).
            page: Page number (1-20). Defaults to 1.
            sort: One of relevant, newest, price_low_to_high, price_high_to_low,
                square_feet, lot_size, price_per_sqft, beds, baths.
            price_min: Minimum price filter.
            price_max: Maximum price filter.
            beds_min: Minimum number of bedrooms.
            baths_min: Minimum number of bathrooms.
            home_type: One of house, condo, townhouse, multi_family, land,
                other, mobile, coop.
            sqft_min: Minimum living area (square feet).
            sqft_max: Maximum living area (square feet).
            lot_min: Minimum lot size (square feet).
            lot_max: Maximum lot size (square feet).
            year_built_min: Minimum year built.
            year_built_max: Maximum year built.
            max_days_on_market: Maximum days on market.
            north: North map bound. Optional bbox override.
            south: South map bound.
            east: East map bound.
            west: West map bound.

        Returns:
            Search response with matching listings, map bounds, and pagination.

        Raises:
            AuthenticationError: If the API key is invalid.
            ValidationError: If the parameters are invalid.

        Example:
            ```python
            results = await client.redfin.search(
                "Austin, TX",
                price_max=750000,
                beds_min=3,
                sort="price_low_to_high",
            )
            print(f"Page {results.pagination.current_page}")
            ```
        """
        params: dict[str, Any] = {
            "location": location,
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
            "max_days_on_market": max_days_on_market,
            "north": north,
            "south": south,
            "east": east,
            "west": west,
        }
        response = await self._client.get("/v1/redfin/search", params=params)
        return SearchResponse.model_validate(response)

    async def get_property(
        self,
        property_id: str | None = None,
        *,
        url: str | None = None,
    ) -> PropertyResponse:
        """Get a single Redfin property's full detail by id or URL.

        Provide either ``property_id`` or ``url``.

        Args:
            property_id: The Redfin property id.
            url: Full Redfin home URL.

        Returns:
            Property detail response.

        Raises:
            NotFoundError: If the property doesn't exist.
            AuthenticationError: If the API key is invalid.
            ValidationError: If neither property_id nor url is provided.

        Example:
            ```python
            detail = await client.redfin.get_property("12345678")

            by_url = await client.redfin.get_property(
                url="https://www.redfin.com/.../home/12345678"
            )
            ```
        """
        if url is not None:
            response = await self._client.get("/v1/redfin/property", params={"url": url})
        else:
            response = await self._client.get(f"/v1/redfin/property/{property_id}")
        return PropertyResponse.model_validate(response)

    async def get_agent(
        self,
        agent_id: str | None = None,
        *,
        url: str | None = None,
    ) -> AgentResponse:
        """Get a Redfin agent's profile and their active listings.

        Provide either ``agent_id`` or ``url``.

        Args:
            agent_id: The Redfin agent slug.
            url: Full Redfin agent profile URL.

        Returns:
            Agent profile response with the agent and their listings.

        Raises:
            NotFoundError: If the agent doesn't exist.
            AuthenticationError: If the API key is invalid.
            ValidationError: If neither agent_id nor url is provided.

        Example:
            ```python
            profile = await client.redfin.get_agent("jane-doe")
            for listing in profile.agent.listings:
                print(listing.street_line)
            ```
        """
        params: dict[str, Any] = {"agent_id": agent_id, "url": url}
        response = await self._client.get("/v1/redfin/agent", params=params)
        return AgentResponse.model_validate(response)

    async def autocomplete(self, query: str) -> AutocompleteResponse:
        """Resolve a search term to Redfin locations.

        Args:
            query: Partial location — city, ZIP, address, or neighborhood.

        Returns:
            Autocomplete response with location suggestions.

        Example:
            ```python
            result = await client.redfin.autocomplete("austin")
            for r in result.results:
                print(r.display_name)
            ```
        """
        params: dict[str, Any] = {"query": query}
        response = await self._client.get("/v1/redfin/autocomplete", params=params)
        return AutocompleteResponse.model_validate(response)

    async def list_markets(self) -> MarketsResponse:
        """Get all supported Redfin coverage markets.

        Returns:
            Markets response with all supported markets.

        Example:
            ```python
            result = await client.redfin.list_markets()
            for m in result.markets:
                print(f"{m.code}: {m.name} ({m.domain})")
            ```
        """
        response = await self._client.get("/v1/redfin/markets")
        return MarketsResponse.model_validate(response)
