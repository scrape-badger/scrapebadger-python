"""GoogleClient — top-level aggregator for Google Scraper sub-clients."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.google.ai_mode import AiModeClient
from scrapebadger.google.autocomplete import AutocompleteClient
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

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class GoogleClient:
    """Client for all Google Scraper API operations.

    Groups the 19 Google product APIs into logical sub-clients accessible
    as properties:

    Attributes:
        search: Google Web Search (SERP) — with optional AI Overview follow-up.
        maps: Google Maps (search, places, reviews, photos, posts).
        news: Google News (search, topics, trending).
        hotels: Google Hotels (search, details).
        trends: Google Trends (interest, regions, related, trending, autocomplete).
        jobs: Google Jobs.
        shopping: Google Shopping (search, product details, click enrichment).
        patents: Google Patents (search, details).
        scholar: Google Scholar (search, profiles, author, author citation, cite).
        autocomplete: Google Autocomplete.
        images: Google Images.
        videos: Google Videos.
        finance: Google Finance quotes.
        ai_mode: Google AI Mode (udm=50 answers).
        lens: Google Lens visual search.
        local: Google Local Pack search (tbm=lcl).
        shorts: Google Shorts (short-form video results, udm=39).
        flights: Google Flights (one-way / round-trip / multi-city).
        products: Google Products (immersive product detail).

    Example:
        ```python
        from scrapebadger import ScrapeBadger

        async with ScrapeBadger(api_key="your-key") as client:
            serp = await client.google.search.search("python 3.13")
            maps = await client.google.maps.search("coffee shops san francisco")
            news = await client.google.news.search("openai")

            # New in v0.3: Local Pack, Shorts, Flights, and Scholar depth
            local = await client.google.local.search("pizza in brooklyn")
            shorts = await client.google.shorts.search("cooking hacks")
            flights = await client.google.flights.search(
                departure_id="JFK",
                arrival_id="LHR",
                outbound_date="2026-06-15",
                return_date="2026-06-22",
            )
            profiles = await client.google.scholar.profiles("Geoffrey Hinton")
        ```

    Note:
        This client is not instantiated directly. Access it through the
        `google` property of the main `ScrapeBadger` client.
    """

    def __init__(self, client: BaseClient) -> None:
        self._client = client
        self._search: SearchClient | None = None
        self._maps: MapsClient | None = None
        self._news: NewsClient | None = None
        self._hotels: HotelsClient | None = None
        self._trends: TrendsClient | None = None
        self._jobs: JobsClient | None = None
        self._shopping: ShoppingClient | None = None
        self._patents: PatentsClient | None = None
        self._scholar: ScholarClient | None = None
        self._autocomplete: AutocompleteClient | None = None
        self._images: ImagesClient | None = None
        self._videos: VideosClient | None = None
        self._finance: FinanceClient | None = None
        self._ai_mode: AiModeClient | None = None
        self._lens: LensClient | None = None
        self._shorts: ShortsClient | None = None
        self._flights: FlightsClient | None = None
        self._products: ProductsClient | None = None

    @property
    def search(self) -> SearchClient:
        """Google Web Search (SERP) — organic results, knowledge graph, PAA, related."""
        if self._search is None:
            self._search = SearchClient(self._client)
        return self._search

    @property
    def maps(self) -> MapsClient:
        """Google Maps — place search, details, reviews, photos, posts."""
        if self._maps is None:
            self._maps = MapsClient(self._client)
        return self._maps

    @property
    def news(self) -> NewsClient:
        """Google News — article search, topics, trending stories."""
        if self._news is None:
            self._news = NewsClient(self._client)
        return self._news

    @property
    def hotels(self) -> HotelsClient:
        """Google Hotels — hotel search and property details."""
        if self._hotels is None:
            self._hotels = HotelsClient(self._client)
        return self._hotels

    @property
    def trends(self) -> TrendsClient:
        """Google Trends — interest over time, regions, related queries/topics."""
        if self._trends is None:
            self._trends = TrendsClient(self._client)
        return self._trends

    @property
    def jobs(self) -> JobsClient:
        """Google Jobs — job listings aggregated from the web."""
        if self._jobs is None:
            self._jobs = JobsClient(self._client)
        return self._jobs

    @property
    def shopping(self) -> ShoppingClient:
        """Google Shopping — product search, details, per-product click enrichment."""
        if self._shopping is None:
            self._shopping = ShoppingClient(self._client)
        return self._shopping

    @property
    def patents(self) -> PatentsClient:
        """Google Patents — patent search and document details."""
        if self._patents is None:
            self._patents = PatentsClient(self._client)
        return self._patents

    @property
    def scholar(self) -> ScholarClient:
        """Google Scholar — academic paper search."""
        if self._scholar is None:
            self._scholar = ScholarClient(self._client)
        return self._scholar

    @property
    def autocomplete(self) -> AutocompleteClient:
        """Google Autocomplete — search suggestion lookup."""
        if self._autocomplete is None:
            self._autocomplete = AutocompleteClient(self._client)
        return self._autocomplete

    @property
    def images(self) -> ImagesClient:
        """Google Images — image search."""
        if self._images is None:
            self._images = ImagesClient(self._client)
        return self._images

    @property
    def videos(self) -> VideosClient:
        """Google Videos — video search."""
        if self._videos is None:
            self._videos = VideosClient(self._client)
        return self._videos

    @property
    def finance(self) -> FinanceClient:
        """Google Finance — stock and index quotes."""
        if self._finance is None:
            self._finance = FinanceClient(self._client)
        return self._finance

    @property
    def ai_mode(self) -> AiModeClient:
        """Google AI Mode — generative AI answers (udm=50)."""
        if self._ai_mode is None:
            self._ai_mode = AiModeClient(self._client)
        return self._ai_mode

    @property
    def lens(self) -> LensClient:
        """Google Lens — visual image search."""
        if self._lens is None:
            self._lens = LensClient(self._client)
        return self._lens

    @property
    def shorts(self) -> ShortsClient:
        """Google Shorts — short-form vertical video results (udm=39)."""
        if self._shorts is None:
            self._shorts = ShortsClient(self._client)
        return self._shorts

    @property
    def flights(self) -> FlightsClient:
        """Google Flights — one-way, round-trip, and multi-city itineraries."""
        if self._flights is None:
            self._flights = FlightsClient(self._client)
        return self._flights

    @property
    def products(self) -> ProductsClient:
        """Google Products — immersive product detail."""
        if self._products is None:
            self._products = ProductsClient(self._client)
        return self._products

    # --- BEGIN generated by sdk/codegen/facade — do not edit ---

    async def google_ai_overview_inline_serp_block(
        self, *, q: str, gl: str = "us", hl: str = "en"
    ) -> dict[str, Any]:
        """Google AI Overview (inline SERP block).

        Generated from the OpenAPI spec; returns the raw response dict.
        """
        params = {k: v for k, v in {"q": q, "gl": gl, "hl": hl}.items() if v is not None}
        return await self._client.get("/v1/google/ai-overview", params=params)

    async def google_flights_calendar_cheapest_fare_per_date(
        self,
        *,
        departure_id: str,
        arrival_id: str,
        outbound_date_from: str,
        outbound_date_to: str,
        trip_type: str = "one_way",
        trip_length_days: str | None = None,
        return_date_from: str | None = None,
        return_date_to: str | None = None,
        adults: int = 1,
        children: int = 0,
        infants_in_seat: int = 0,
        infants_on_lap: int = 0,
        travel_class: str = "economy",
        currency: str = "USD",
        gl: str = "us",
        hl: str = "en",
    ) -> dict[str, Any]:
        """Google Flights calendar — cheapest fare per date.

        Generated from the OpenAPI spec; returns the raw response dict.
        """
        params = {
            k: v
            for k, v in {
                "departure_id": departure_id,
                "arrival_id": arrival_id,
                "outbound_date_from": outbound_date_from,
                "outbound_date_to": outbound_date_to,
                "trip_type": trip_type,
                "trip_length_days": trip_length_days,
                "return_date_from": return_date_from,
                "return_date_to": return_date_to,
                "adults": adults,
                "children": children,
                "infants_in_seat": infants_in_seat,
                "infants_on_lap": infants_on_lap,
                "travel_class": travel_class,
                "currency": currency,
                "gl": gl,
                "hl": hl,
            }.items()
            if v is not None
        }
        return await self._client.get("/v1/google/flights/calendar", params=params)

    # --- END generated by sdk/codegen/facade ---
