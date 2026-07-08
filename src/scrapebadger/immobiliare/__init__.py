"""Immobiliare API module for ScrapeBadger SDK.

This module provides an async client for scraping Immobiliare-group
real-estate data (immobiliare.it, indomio.es, indomio.gr, immotop.lu) through
the ScrapeBadger API. Endpoints: autocomplete, search, listing detail, agency
profile + listings, price stats (€/m² time series), markets, and reference.
All methods are async and return strongly-typed Pydantic models.

Example:
    ```python
    from scrapebadger import ScrapeBadger

    async with ScrapeBadger(api_key="your-key") as client:
        # Resolve a place, then search it
        hits = await client.immobiliare.autocomplete("Milano")
        city = hits.suggestions[0]
        results = await client.immobiliare.search(city_id=city.city_id, price_max=500000)
        for listing in results.listings:
            print(f"{listing.id}: {listing.title}")

        # Full listing detail
        detail = await client.immobiliare.get_listing(123456789)
        print(detail.description)
    ```
"""

from scrapebadger.immobiliare.client import ImmobiliareClient
from scrapebadger.immobiliare.models import (
    Agency,
    AgencyAgent,
    AgencyListingsResponse,
    AgencyProfile,
    Agent,
    Feature,
    Listing,
    Location,
    Market,
    Photo,
    Price,
    PriceStatsPoint,
    PriceStatsResponse,
    PropertyUnit,
    ReferenceResponse,
    RelatedSearch,
    SearchResponse,
    Suggestion,
    SuggestResponse,
)

__all__ = [
    # Shared / nested models
    "Agency",
    "AgencyAgent",
    # Response envelopes
    "AgencyListingsResponse",
    "AgencyProfile",
    "Agent",
    "Feature",
    # Client
    "ImmobiliareClient",
    "Listing",
    "Location",
    "Market",
    "Photo",
    "Price",
    "PriceStatsPoint",
    "PriceStatsResponse",
    "PropertyUnit",
    "ReferenceResponse",
    "RelatedSearch",
    "SearchResponse",
    "SuggestResponse",
    "Suggestion",
]
