"""Apple App Store API module for ScrapeBadger SDK.

This module provides an async client for scraping the Apple App Store through
the ScrapeBadger API. All methods are async and return strongly-typed Pydantic
models.

Example:
    ```python
    from scrapebadger import ScrapeBadger

    async with ScrapeBadger(api_key="your-key") as client:
        # Search
        results = await client.app_store.search("slack")
        for app in results.apps:
            print(f"{app.app_id} — {app.name}")

        # Full app detail (iTunes + storefront enrichment)
        app = await client.app_store.get_app("618783545")
        print(app.version, app.extras.has_in_app_purchases)

        # Top charts
        chart = await client.app_store.charts(type="top-free")
    ```
"""

from scrapebadger.app_store.client import AppStoreClient
from scrapebadger.app_store.models import (
    App,
    AppExtras,
    ChartEntry,
    ChartsResponse,
    Developer,
    DeveloperResponse,
    Genre,
    GenresResponse,
    InAppPurchase,
    Market,
    MarketsResponse,
    PrivacyType,
    RatingHistogram,
    Review,
    ReviewsResponse,
    Screenshot,
    SearchResponse,
)

__all__ = [
    # App
    "App",
    "AppExtras",
    # Client
    "AppStoreClient",
    # Charts
    "ChartEntry",
    "ChartsResponse",
    # Developer
    "Developer",
    "DeveloperResponse",
    # Reference
    "Genre",
    "GenresResponse",
    # Storefront value objects
    "InAppPurchase",
    "Market",
    "MarketsResponse",
    "PrivacyType",
    "RatingHistogram",
    # Reviews
    "Review",
    "ReviewsResponse",
    "Screenshot",
    # Search
    "SearchResponse",
]
