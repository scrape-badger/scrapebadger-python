"""Apartments.com API module for ScrapeBadger SDK.

Async client for US rental listings from apartments.com, with unit-level
pricing: every rentable unit's rent, beds, baths, square footage and
availability date.

Example:
    ```python
    from scrapebadger import ScrapeBadger

    async with ScrapeBadger(api_key="your-key") as client:
        page = await client.apartments.search("kansas-city-mo", beds=1)
        prop = await client.apartments.get_property(page.results[0].url)
        for unit in prop.units:
            print(unit.unit_number, unit.rent, unit.available_text)
    ```
"""

from scrapebadger.apartments.client import ApartmentsClient
from scrapebadger.apartments.models import (
    FloorPlan,
    Property,
    SearchResponse,
    SearchResult,
    Unit,
)

__all__ = [
    "ApartmentsClient",
    "FloorPlan",
    "Property",
    "SearchResponse",
    "SearchResult",
    "Unit",
]
