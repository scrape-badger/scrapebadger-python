"""Zillow API module for ScrapeBadger SDK.

This module provides a comprehensive async client for scraping real-estate
listings, property detail, and agent profiles from zillow.com through the
ScrapeBadger API. Zillow is a single-domain target (US + Canadian inventory,
USD, en-US). All methods are async and return strongly-typed Pydantic models.

Example:
    ```python
    from scrapebadger import ScrapeBadger

    async with ScrapeBadger(api_key="your-key") as client:
        # Search for listings
        results = await client.zillow.search.search("Austin, TX")
        for listing in results.results:
            print(listing.zpid, listing.price)

        # Get property detail
        prop = await client.zillow.properties.get_property("2078133351")
        print(prop.bedrooms, prop.bathrooms, prop.living_area)

        # Get an agent profile + their listings
        agent = await client.zillow.agents.get_agent(username="jane-doe")
    ```
"""

from scrapebadger.zillow.client import ZillowClient
from scrapebadger.zillow.models import (
    Address,
    Agent,
    AgentAttribution,
    AgentLicense,
    AgentResponse,
    AgentReview,
    AutocompleteResponse,
    AutocompleteResult,
    HomeFacts,
    LatLong,
    Listing,
    ListingSubType,
    MapBounds,
    MarketInfo,
    MarketsResponse,
    MortgageRate,
    MortgageRates,
    NearbyRegion,
    OpenHouse,
    Pagination,
    PastSale,
    Photo,
    PriceHistoryEvent,
    Property,
    PropertyResponse,
    RegionSelection,
    School,
    SearchResponse,
    TaxHistoryEvent,
    ZestimateHistoryPoint,
)

__all__ = [
    "Address",
    "Agent",
    "AgentAttribution",
    "AgentLicense",
    "AgentResponse",
    "AgentReview",
    "AutocompleteResponse",
    "AutocompleteResult",
    "HomeFacts",
    "LatLong",
    "Listing",
    "ListingSubType",
    "MapBounds",
    "MarketInfo",
    "MarketsResponse",
    "MortgageRate",
    "MortgageRates",
    "NearbyRegion",
    "OpenHouse",
    "Pagination",
    "PastSale",
    "Photo",
    "PriceHistoryEvent",
    "Property",
    "PropertyResponse",
    "RegionSelection",
    "School",
    "SearchResponse",
    "TaxHistoryEvent",
    "ZestimateHistoryPoint",
    "ZillowClient",
]
