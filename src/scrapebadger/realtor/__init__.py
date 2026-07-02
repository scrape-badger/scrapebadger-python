"""Realtor API module for ScrapeBadger SDK.

This module provides a comprehensive async client for scraping real-estate
listings through the ScrapeBadger API, unifying realtor.com (US) and
realtor.ca (Canada) behind a single ``market`` parameter. All methods are
async and return strongly-typed Pydantic models.

Example:
    ```python
    from scrapebadger import ScrapeBadger

    async with ScrapeBadger(api_key="your-key") as client:
        # Search for listings
        results = await client.realtor.search.search("Austin, TX")
        for prop in results.results:
            print(prop.property_id, prop.list_price)

        # Get property detail
        detail = await client.realtor.properties.get_property("1234567890")
        print(detail.beds, detail.baths, detail.sqft)
    ```
"""

from scrapebadger.realtor.client import RealtorClient
from scrapebadger.realtor.models import (
    Address,
    Agent,
    AutocompleteResponse,
    Coordinate,
    DetailGroup,
    Estimate,
    Flags,
    MarketInfo,
    MarketsResponse,
    Office,
    OpenHouse,
    Phone,
    Photo,
    PriceEvent,
    Property,
    PropertyDetail,
    School,
    SearchResponse,
    Suggestion,
    TaxRecord,
)

__all__ = [
    "Address",
    "Agent",
    "AutocompleteResponse",
    "Coordinate",
    "DetailGroup",
    "Estimate",
    "Flags",
    "MarketInfo",
    "MarketsResponse",
    "Office",
    "OpenHouse",
    "Phone",
    "Photo",
    "PriceEvent",
    "Property",
    "PropertyDetail",
    "RealtorClient",
    "School",
    "SearchResponse",
    "Suggestion",
    "TaxRecord",
]
