"""Redfin API module for ScrapeBadger SDK.

This module provides an async client for scraping Redfin real-estate data
through the ScrapeBadger API. All methods are async and return strongly-typed
Pydantic models.

Example:
    ```python
    from scrapebadger import ScrapeBadger

    async with ScrapeBadger(api_key="your-key") as client:
        # Search for-sale listings
        results = await client.redfin.search("Austin, TX")
        for listing in results.results:
            print(f"{listing.position}. {listing.street_line}")

        # Get property detail
        detail = await client.redfin.get_property("12345678")
        print(detail.property.price)

        # Get an agent profile
        agent = await client.redfin.get_agent("jane-doe")
        print(agent.agent.name)
    ```
"""

from scrapebadger.redfin.client import RedfinClient
from scrapebadger.redfin.models import (
    Address,
    Agent,
    AgentResponse,
    AgentReview,
    AmenityGroup,
    AutocompleteResponse,
    AutocompleteResult,
    DataSource,
    LatLong,
    Listing,
    MapBounds,
    MarketInfo,
    MarketsResponse,
    Pagination,
    Photo,
    PriceHistoryEvent,
    Property,
    PropertyResponse,
    RegionSelection,
    Sash,
    School,
    SearchMedian,
    SearchResponse,
    TaxHistoryEvent,
)

__all__ = [
    # Property detail nested
    "Address",
    # Agent
    "Agent",
    "AgentResponse",
    "AgentReview",
    "AmenityGroup",
    # Autocomplete
    "AutocompleteResponse",
    "AutocompleteResult",
    "DataSource",
    # Shared
    "LatLong",
    # Search
    "Listing",
    "MapBounds",
    "MarketInfo",
    "MarketsResponse",
    "Pagination",
    "Photo",
    "PriceHistoryEvent",
    "Property",
    "PropertyResponse",
    # Client
    "RedfinClient",
    "RegionSelection",
    "Sash",
    "School",
    "SearchMedian",
    "SearchResponse",
    "TaxHistoryEvent",
]
