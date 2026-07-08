"""LoopNet API module for ScrapeBadger SDK.

This module provides a comprehensive async client for scraping LoopNet
commercial-real-estate data through the ScrapeBadger API. All methods are
async and return strongly-typed Pydantic models.

Example:
    ```python
    from scrapebadger import ScrapeBadger

    async with ScrapeBadger(api_key="your-key") as client:
        # Search listings
        results = await client.loopnet.search.search("Houston, TX")
        for card in results.results:
            print(f"{card.position}. {card.address}")

        # Get listing detail
        detail = await client.loopnet.listings.get("12345678")
        print(detail.listing.price_text)

        # Get a broker profile
        broker = await client.loopnet.brokers.get("jane-doe", "w7x123")
        print(broker.broker.name)
    ```
"""

from scrapebadger.loopnet.client import LoopNetClient
from scrapebadger.loopnet.models import (
    Broker,
    BrokerProfile,
    BrokerResponse,
    ListingCard,
    ListingDetail,
    ListingResponse,
    MarketInfo,
    MarketsResponse,
    Pagination,
    PropertyTypeInfo,
    PropertyTypesResponse,
    SearchResponse,
    Space,
)

__all__ = [
    # Brokers
    "Broker",
    "BrokerProfile",
    "BrokerResponse",
    # Search
    "ListingCard",
    # Listing detail
    "ListingDetail",
    "ListingResponse",
    # Client
    "LoopNetClient",
    # Reference
    "MarketInfo",
    "MarketsResponse",
    "Pagination",
    "PropertyTypeInfo",
    "PropertyTypesResponse",
    "SearchResponse",
    "Space",
]
