"""Google Ads Transparency Center API module for ScrapeBadger SDK.

This module provides an async client for the Google Ads Transparency Center
through the ScrapeBadger API. All methods are async and return strongly-typed
Pydantic models.

Example:
    ```python
    from scrapebadger import ScrapeBadger

    async with ScrapeBadger(api_key="your-key") as client:
        # Resolve a domain to advertiser IDs
        found = await client.google_ads.search_advertisers("tesla.com")
        advertiser_id = found.advertisers[0].advertiser_id

        # Their creatives
        ads = await client.google_ads.search_ads(advertiser_id=advertiser_id)
        for creative in ads.creatives:
            print(creative.creative_id, creative.format)

        # Disclosed spend
        profile = await client.google_ads.get_advertiser(advertiser_id)
    ```
"""

from scrapebadger.google_ads.client import GoogleAdsClient
from scrapebadger.google_ads.models import (
    AdCreative,
    AdCreativeResponse,
    AdsSearchResponse,
    AdvertiserAdMix,
    AdvertiserResponse,
    AdvertiserSpendPoint,
    AdvertisersResponse,
    AdvertiserSuggestion,
    AppliedFilters,
    CreativeVariation,
    PoliticalDisclosure,
    PoliticalRegionSpend,
)

__all__ = [
    # Creatives
    "AdCreative",
    "AdCreativeResponse",
    "AdsSearchResponse",
    # Advertisers
    "AdvertiserAdMix",
    "AdvertiserResponse",
    "AdvertiserSpendPoint",
    "AdvertiserSuggestion",
    "AdvertisersResponse",
    "AppliedFilters",
    "CreativeVariation",
    # Client
    "GoogleAdsClient",
    # Political disclosure
    "PoliticalDisclosure",
    "PoliticalRegionSpend",
]
