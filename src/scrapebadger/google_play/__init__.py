"""Google Play Store API module for ScrapeBadger SDK.

This module provides an async client for scraping the Google Play Store
through the ScrapeBadger API. All methods are async and return strongly-typed
Pydantic models.

Example:
    ```python
    from scrapebadger import ScrapeBadger

    async with ScrapeBadger(api_key="your-key") as client:
        # Search
        results = await client.google_play.search("puzzle")
        for card in results.apps:
            print(f"{card.app_id} — {card.title}")

        # Full app detail
        app = await client.google_play.get_app("com.whatsapp")
        print(app.installs, app.developer.legal_name)

        # Reviews
        page = await client.google_play.get_reviews("com.whatsapp")
    ```
"""

from scrapebadger.google_play.client import GooglePlayClient
from scrapebadger.google_play.models import (
    App,
    AppCard,
    AppListResponse,
    CategoriesResponse,
    Category,
    ChartRank,
    DataSafetySection,
    Developer,
    Market,
    MarketsResponse,
    PermissionGroup,
    PermissionsResponse,
    Price,
    RatingHistogram,
    Review,
    ReviewsResponse,
)

__all__ = [
    # Apps
    "App",
    "AppCard",
    "AppListResponse",
    # Reference
    "CategoriesResponse",
    "Category",
    "ChartRank",
    "DataSafetySection",
    "Developer",
    # Client
    "GooglePlayClient",
    "Market",
    "MarketsResponse",
    # Permissions
    "PermissionGroup",
    "PermissionsResponse",
    "Price",
    "RatingHistogram",
    # Reviews
    "Review",
    "ReviewsResponse",
]
