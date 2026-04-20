"""Google Scraper API client for ScrapeBadger.

Provides access to all 19 Google product APIs:

- Google Search / SERP (with optional deferred AI Overview follow-up)
- Google Maps (search, place details, reviews, photos, posts)
- Google News (search, topics, trending)
- Google Hotels (search, details)
- Google Trends (interest, regions, related, trending, topic autocomplete)
- Google Jobs
- Google Shopping (search, product details, per-product merchant URL enrichment)
- Google Patents (search, details)
- Google Scholar (search, profiles, author, author citation, cite formats)
- Google Autocomplete
- Google Images
- Google Videos
- Google Finance
- Google AI Mode
- Google Lens
- Google Local (Local Pack business listings for SERP-intent queries)
- Google Shorts (short-form vertical video results)
- Google Flights (one-way / round-trip / multi-city)
- Google Products (immersive product detail)

Example:
    ```python
    from scrapebadger import ScrapeBadger

    async with ScrapeBadger(api_key="your-key") as client:
        # Web search
        serp = await client.google.search.search("python 3.13")
        for result in serp["organic_results"]:
            print(result["title"], result["link"])

        # Maps search
        places = await client.google.maps.search("pizza in New York")

        # Shopping search + per-product click enrichment
        products = await client.google.shopping.search("laptop")
        first = products["results"][0]
        enrich = await client.google.shopping.click(
            title=first["title"],
            source=first["source"],
        )
        print("Merchant URL:", enrich["merchant_url"])

        # Flights
        flights = await client.google.flights.search(
            departure_id="JFK",
            arrival_id="LHR",
            outbound_date="2026-06-15",
            return_date="2026-06-22",
        )
    ```
"""

from scrapebadger.google.ai_mode import AiModeClient
from scrapebadger.google.autocomplete import AutocompleteClient
from scrapebadger.google.client import GoogleClient
from scrapebadger.google.finance import FinanceClient
from scrapebadger.google.flights import FlightsClient
from scrapebadger.google.hotels import HotelsClient
from scrapebadger.google.images import ImagesClient
from scrapebadger.google.jobs import JobsClient
from scrapebadger.google.lens import LensClient
from scrapebadger.google.maps import MapsClient
from scrapebadger.google.news import NewsClient
from scrapebadger.google.patents import PatentsClient
from scrapebadger.google.products import ProductsClient
from scrapebadger.google.scholar import ScholarClient
from scrapebadger.google.search import SearchClient
from scrapebadger.google.shopping import ShoppingClient
from scrapebadger.google.shorts import ShortsClient
from scrapebadger.google.trends import TrendsClient
from scrapebadger.google.videos import VideosClient

__all__ = [
    "AiModeClient",
    "AutocompleteClient",
    "FinanceClient",
    "FlightsClient",
    "GoogleClient",
    "HotelsClient",
    "ImagesClient",
    "JobsClient",
    "LensClient",
    "MapsClient",
    "NewsClient",
    "PatentsClient",
    "ProductsClient",
    "ScholarClient",
    "SearchClient",
    "ShoppingClient",
    "ShortsClient",
    "TrendsClient",
    "VideosClient",
]
