"""Main ScrapeBadger client.

This module provides the main entry point for the ScrapeBadger SDK.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from scrapebadger._internal.client import BaseClient
from scrapebadger._internal.config import ClientConfig
from scrapebadger.amazon.client import AmazonClient
from scrapebadger.apartments.client import ApartmentsClient
from scrapebadger.chatgpt.client import ChatGPTClient
from scrapebadger.depop.client import DepopClient
from scrapebadger.ebay.client import EbayClient
from scrapebadger.google.client import GoogleClient
from scrapebadger.immobiliare.client import ImmobiliareClient
from scrapebadger.instagram.client import InstagramClient
from scrapebadger.leboncoin.client import LeboncoinClient
from scrapebadger.linkedin.client import LinkedInClient
from scrapebadger.loopnet.client import LoopNetClient
from scrapebadger.realtor.client import RealtorClient
from scrapebadger.reddit.client import RedditClient
from scrapebadger.redfin.client import RedfinClient
from scrapebadger.tiktok.client import TikTokClient
from scrapebadger.twitter.client import TwitterClient
from scrapebadger.vinted.client import VintedClient
from scrapebadger.walmart.client import WalmartClient
from scrapebadger.web.client import WebClient
from scrapebadger.youtube.client import YoutubeClient
from scrapebadger.zillow.client import ZillowClient

if TYPE_CHECKING:
    from types import TracebackType


class ScrapeBadger:
    """Main ScrapeBadger SDK client.

    This is the primary entry point for the ScrapeBadger SDK. It provides
    access to all supported scrapers through a unified, async-first interface.

    The client should be used as an async context manager to ensure proper
    resource cleanup:

    ```python
    async with ScrapeBadger(api_key="your-key") as client:
        user = await client.twitter.users.get_by_username("elonmusk")
    ```

    Alternatively, you can manage the client lifecycle manually:

    ```python
    client = ScrapeBadger(api_key="your-key")
    try:
        user = await client.twitter.users.get_by_username("elonmusk")
    finally:
        await client.close()
    ```

    Attributes:
        twitter: Client for Twitter scraping operations.

    Example:
        ```python
        import asyncio
        from scrapebadger import ScrapeBadger

        async def main():
            async with ScrapeBadger(api_key="your-api-key") as client:
                # Twitter operations
                user = await client.twitter.users.get_by_username("elonmusk")
                print(f"{user.name}: {user.followers_count:,} followers")

                tweets = await client.twitter.tweets.search("python")
                for tweet in tweets.data:
                    print(f"- {tweet.text[:100]}...")

        asyncio.run(main())
        ```

    Args:
        api_key: Your ScrapeBadger API key. Get one at https://scrapebadger.com
        base_url: Override the API base URL (for testing or self-hosted).
        timeout: Request timeout in seconds (default: 300s / 5 minutes).
        max_retries: Maximum retry attempts for failed requests (default: 3).
        config: Advanced configuration. If provided, other args are ignored.
    """

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        config: ClientConfig | None = None,
    ) -> None:
        """Initialize the ScrapeBadger client.

        Args:
            api_key: Your ScrapeBadger API key.
            base_url: Override the API base URL.
            timeout: Request timeout in seconds.
            max_retries: Maximum retry attempts.
            config: Advanced configuration object.

        Raises:
            ValueError: If no API key is provided.
        """
        if config is not None:
            self._config = config
        else:
            if api_key is None:
                msg = "API key is required. Get one at https://scrapebadger.com"
                raise ValueError(msg)

            kwargs: dict[str, object] = {"api_key": api_key}
            if base_url is not None:
                kwargs["base_url"] = base_url
            if timeout is not None:
                kwargs["timeout"] = timeout
            if max_retries is not None:
                kwargs["max_retries"] = max_retries

            self._config = ClientConfig(**kwargs)  # type: ignore[arg-type]

        self._base_client = BaseClient(self._config)
        self._twitter: TwitterClient | None = None
        self._vinted: VintedClient | None = None
        self._web: WebClient | None = None
        self._google: GoogleClient | None = None
        self._reddit: RedditClient | None = None
        self._redfin: RedfinClient | None = None
        self._apartments: ApartmentsClient | None = None
        self._depop: DepopClient | None = None
        self._linkedin: LinkedInClient | None = None
        self._amazon: AmazonClient | None = None
        self._ebay: EbayClient | None = None
        self._youtube: YoutubeClient | None = None
        self._tiktok: TikTokClient | None = None
        self._realtor: RealtorClient | None = None
        self._zillow: ZillowClient | None = None
        self._leboncoin: LeboncoinClient | None = None
        self._immobiliare: ImmobiliareClient | None = None
        self._loopnet: LoopNetClient | None = None
        self._chatgpt: ChatGPTClient | None = None
        self._instagram: InstagramClient | None = None
        self._walmart: WalmartClient | None = None

    @property
    def config(self) -> ClientConfig:
        """Get the client configuration."""
        return self._config

    @property
    def web(self) -> WebClient:
        """Access web scraping operations.

        Returns:
            WebClient providing access to scrape, screenshot, extract, batch, and sessions.
        """
        if self._web is None:
            self._web = WebClient(self._base_client)
        return self._web

    @property
    def twitter(self) -> TwitterClient:
        """Access Twitter scraping operations.

        Returns:
            TwitterClient providing access to all Twitter endpoints.

        Example:
            ```python
            # Access Twitter through the property
            user = await client.twitter.users.get_by_username("elonmusk")
            tweets = await client.twitter.tweets.search("python")
            ```
        """
        if self._twitter is None:
            self._twitter = TwitterClient(self._base_client)
        return self._twitter

    @property
    def vinted(self) -> VintedClient:
        """Access Vinted scraping operations.

        Returns:
            VintedClient providing access to all Vinted endpoints.

        Example:
            ```python
            # Search for items
            results = await client.vinted.search.search("nike air max")

            # Get item details
            detail = await client.vinted.items.get(123456789)

            # Get user profile
            profile = await client.vinted.users.get_profile(12345)
            ```
        """
        if self._vinted is None:
            self._vinted = VintedClient(self._base_client)
        return self._vinted

    @property
    def reddit(self) -> RedditClient:
        """Access Reddit scraping operations.

        Returns:
            RedditClient providing access to all Reddit endpoints.

        Example:
            ```python
            # Search posts
            results = await client.reddit.search.posts("python asyncio")

            # Get subreddit hot posts
            hot = await client.reddit.subreddits.posts("python", sort="hot")

            # Get user profile
            profile = await client.reddit.users.get("spez")
            ```
        """
        if self._reddit is None:
            self._reddit = RedditClient(self._base_client)
        return self._reddit

    @property
    def apartments(self) -> ApartmentsClient:
        """Access Apartments.com Scraper API operations.

        Returns:
            ApartmentsClient providing search and property detail with
            unit-level pricing. Single market: apartments.com (US, USD, en-US).

        Example:
            ```python
            page = await client.apartments.search("kansas-city-mo", beds=1)
            prop = await client.apartments.get_property(page.results[0].url)
            ```
        """
        if self._apartments is None:
            self._apartments = ApartmentsClient(self._base_client)
        return self._apartments

    @property
    def instagram(self) -> InstagramClient:
        """Access Instagram scraping operations.

        Returns:
            InstagramClient providing access to all Instagram endpoints.

        Example:
            ```python
            # Get a user profile
            profile = await client.instagram.users.get("instagram")

            # Get a user's posts
            posts = await client.instagram.users.posts("instagram", amount=12)

            # Get media comments
            comments = await client.instagram.media.comments("C1abcdEfGhI")
            ```
        """
        if self._instagram is None:
            self._instagram = InstagramClient(self._base_client)
        return self._instagram

    @property
    def redfin(self) -> RedfinClient:
        """Access Redfin Scraper API operations.

        Returns:
            RedfinClient providing access to all Redfin endpoints (search,
            property detail, agent profile, autocomplete, markets).
            Single market: redfin.com (US, USD, en-US).

        Example:
            ```python
            results = await client.redfin.search("Austin, TX")
            detail = await client.redfin.get_property("12345678")
            agent = await client.redfin.get_agent("jane-doe")
            markets = await client.redfin.list_markets()
            ```
        """
        if self._redfin is None:
            self._redfin = RedfinClient(self._base_client)
        return self._redfin

    @property
    def depop(self) -> DepopClient:
        """Access Depop Scraper API operations.

        Returns:
            DepopClient providing access to all Depop endpoints (search,
            product detail, shop profile, user products, markets). Depop is a
            second-hand fashion marketplace: one global host (depop.com)
            localised by market (us, gb [alias uk], au, ie, it, fr, de, es, nl,
            nz) → country/currency.

        Example:
            ```python
            results = await client.depop.search("nike vintage")
            detail = await client.depop.get_product("some-product-slug")
            shop = await client.depop.get_user("someseller")
            markets = await client.depop.list_markets()
            ```
        """
        if self._depop is None:
            self._depop = DepopClient(self._base_client)
        return self._depop

    @property
    def linkedin(self) -> LinkedInClient:
        """Access LinkedIn Scraper API operations.

        Returns:
            LinkedInClient providing access to LinkedIn's public no-auth
            surface: the guest Jobs API (jobs_search, get_job, company_jobs),
            public company/school/profile SSR pages, public posts / Pulse
            articles / Learning courses, and a geo/company id helper. Deep
            logged-in data is auth-gated and not available.

        Example:
            ```python
            jobs = await client.linkedin.jobs_search(keywords="python", location="Berlin")
            company = await client.linkedin.get_company("microsoft")
            profile = await client.linkedin.get_profile("williamhgates")
            geo = await client.linkedin.geo_suggest("London")
            ```
        """
        if self._linkedin is None:
            self._linkedin = LinkedInClient(self._base_client)
        return self._linkedin

    @property
    def google(self) -> GoogleClient:
        """Access Google Scraper API operations.

        Returns:
            GoogleClient providing access to all 19 Google product APIs.

        Example:
            ```python
            # Web search
            serp = await client.google.search.search("python 3.13")

            # Maps search
            places = await client.google.maps.search("coffee shops sf")

            # Shopping search + merchant URL enrichment
            products = await client.google.shopping.search("laptop")
            enrich = await client.google.shopping.click(
                title=products["results"][0]["title"],
                source=products["results"][0]["source"],
            )
            ```
        """
        if self._google is None:
            self._google = GoogleClient(self._base_client)
        return self._google

    @property
    def amazon(self) -> AmazonClient:
        """Access Amazon Scraper API operations.

        Returns:
            AmazonClient providing access to all 14 Amazon endpoints.

        Example:
            ```python
            # Search for products
            results = await client.amazon.search.search("wireless headphones")

            # Get product detail
            detail = await client.amazon.products.get("B08N5WRWNW")

            # Get bestsellers
            top = await client.amazon.listings.bestsellers(category="electronics")

            # Get a seller profile
            seller = await client.amazon.sellers.get("A2L77EE7U53NWQ")
            ```
        """
        if self._amazon is None:
            self._amazon = AmazonClient(self._base_client)
        return self._amazon

    @property
    def ebay(self) -> EbayClient:
        """Access eBay Scraper API operations.

        Returns:
            EbayClient providing access to all 12 eBay endpoints.

        Example:
            ```python
            # Search for listings
            results = await client.ebay.search.search("nintendo switch")

            # Get item detail
            detail = await client.ebay.items.get_item("123456789012")

            # Browse a category
            cat = await client.ebay.categories.browse_category("9355")

            # Get a seller profile
            seller = await client.ebay.sellers.get_seller("musicmagpie")
            ```
        """
        if self._ebay is None:
            self._ebay = EbayClient(self._base_client)
        return self._ebay

    @property
    def walmart(self) -> WalmartClient:
        """Access Walmart Scraper API operations.

        Returns:
            WalmartClient providing access to all 11 Walmart endpoints.
            US-only: walmart.com is the single supported market.

        Example:
            ```python
            # Search
            results = await client.walmart.search.search("laptop")

            # Product detail
            product = await client.walmart.products.get_product("5689919121")

            # Seller profile
            seller = await client.walmart.sellers.get_seller("101040442")

            # Store detail
            store = await client.walmart.stores.get_store("100")
            ```
        """
        if self._walmart is None:
            self._walmart = WalmartClient(self._base_client)
        return self._walmart

    @property
    def youtube(self) -> YoutubeClient:
        """Access YouTube Scraper API operations.

        Returns:
            YoutubeClient providing access to all YouTube endpoints (search,
            videos, channels, playlists, comments, transcripts, trending,
            shorts, community, music, reference).

        Example:
            ```python
            results = await client.youtube.search.search("lofi hip hop")
            video = await client.youtube.videos.get_video("dQw4w9WgXcQ")
            channel = await client.youtube.channels.get_channel("@mkbhd")
            ```
        """
        if self._youtube is None:
            self._youtube = YoutubeClient(self._base_client)
        return self._youtube

    @property
    def realtor(self) -> RealtorClient:
        """Access Realtor Scraper API operations.

        Returns:
            RealtorClient providing access to all 4 Realtor endpoints
            (search, property detail, autocomplete, markets) across
            realtor.com (US) and realtor.ca (Canada).

        Example:
            ```python
            results = await client.realtor.search.search("Austin, TX")
            detail = await client.realtor.properties.get_property("1234567890")
            hits = await client.realtor.search.autocomplete("toronto", market="ca")
            markets = await client.realtor.reference.list_markets()
            ```
        """
        if self._realtor is None:
            self._realtor = RealtorClient(self._base_client)
        return self._realtor

    @property
    def zillow(self) -> ZillowClient:
        """Access Zillow Scraper API operations.

        Returns:
            ZillowClient providing access to all 5 Zillow endpoints
            (search, property detail, agent profile, autocomplete, markets)
            on zillow.com (US + Canadian inventory).

        Example:
            ```python
            results = await client.zillow.search.search("Austin, TX")
            prop = await client.zillow.properties.get_property("2078133351")
            agent = await client.zillow.agents.get_agent(username="jane-doe")
            hits = await client.zillow.search.autocomplete("austin")
            markets = await client.zillow.reference.list_markets()
            ```
        """
        if self._zillow is None:
            self._zillow = ZillowClient(self._base_client)
        return self._zillow

    @property
    def leboncoin(self) -> LeboncoinClient:
        """Access Leboncoin Scraper API operations.

        Returns:
            LeboncoinClient providing access to all 10 Leboncoin endpoints
            (search, ad detail, similar ads, seller profile/listings,
            categories, regions, departments, location search, markets).

        Example:
            ```python
            # Search for ads
            results = await client.leboncoin.search.search("velo")

            # Get ad detail
            detail = await client.leboncoin.ads.get_ad(2812345678)

            # Get a seller profile
            seller = await client.leboncoin.sellers.get_seller("12345678")

            # Reference regions
            regions = await client.leboncoin.reference.list_regions()
            ```
        """
        if self._leboncoin is None:
            self._leboncoin = LeboncoinClient(self._base_client)
        return self._leboncoin

    @property
    def immobiliare(self) -> ImmobiliareClient:
        """Access Immobiliare Scraper API operations.

        Returns:
            ImmobiliareClient providing access to all Immobiliare-group
            endpoints (autocomplete, search, listing detail, agency
            profile/listings, price stats, markets, reference) across
            immobiliare.it, indomio.es, indomio.gr, and immotop.lu.

        Example:
            ```python
            hits = await client.immobiliare.autocomplete("Milano")
            results = await client.immobiliare.search(location="Milano")
            detail = await client.immobiliare.get_listing(123456789)
            markets = await client.immobiliare.list_markets()
            ```
        """
        if self._immobiliare is None:
            self._immobiliare = ImmobiliareClient(self._base_client)
        return self._immobiliare

    @property
    def loopnet(self) -> LoopNetClient:
        """Access LoopNet Scraper API operations.

        Returns:
            LoopNetClient providing access to all LoopNet commercial-real-estate
            endpoints (search, listing detail, broker profile, markets, property
            types) across loopnet.com/.ca/.co.uk/.fr/.es (US/CA/UK/FR/ES).

        Example:
            ```python
            results = await client.loopnet.search.search("Houston, TX")
            detail = await client.loopnet.listings.get("12345678")
            broker = await client.loopnet.brokers.get("jane-doe", "w7x123")
            markets = await client.loopnet.reference.markets()
            ```
        """
        if self._loopnet is None:
            self._loopnet = LoopNetClient(self._base_client)
        return self._loopnet

    @property
    def chatgpt(self) -> ChatGPTClient:
        """Access ChatGPT Scraper API operations.

        Prompts the real chatgpt.com — not the OpenAI API — anonymously, and
        returns the answer as structured JSON including the web sources
        ChatGPT cited.

        Returns:
            ChatGPTClient providing access to ask, brand-visibility, and
            reference endpoints.

        Example:
            ```python
            result = await client.chatgpt.ask.ask("best running shoes 2026")
            brand = await client.chatgpt.brand.visibility(
                "best web scraping API",
                brand="ScrapeBadger",
                competitors=["Bright Data"],
            )
            models = await client.chatgpt.reference.models()
            ```
        """
        if self._chatgpt is None:
            self._chatgpt = ChatGPTClient(self._base_client)
        return self._chatgpt

    @property
    def tiktok(self) -> TikTokClient:
        """Access TikTok Scraper API operations.

        Returns:
            TikTokClient providing access to all 25 TikTok endpoints.

        Example:
            ```python
            # Get a user profile
            profile = await client.tiktok.users.get_profile("charlidamelio")

            # Get video detail
            video = await client.tiktok.videos.get_detail("7212345678901234567")

            # Search videos
            results = await client.tiktok.search.videos("cooking")

            # Trending songs
            songs = await client.tiktok.trending.songs(region="GB")
            ```
        """
        if self._tiktok is None:
            self._tiktok = TikTokClient(self._base_client)
        return self._tiktok

    async def close(self) -> None:
        """Close the client and release resources.

        This method should be called when you're done using the client.
        If using the client as a context manager, this is called automatically.

        Example:
            ```python
            client = ScrapeBadger(api_key="key")
            try:
                # Use client...
                pass
            finally:
                await client.close()
            ```
        """
        await self._base_client.close()

    async def __aenter__(self) -> ScrapeBadger:
        """Enter async context manager."""
        await self._base_client._get_client()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit async context manager."""
        await self.close()

    def __repr__(self) -> str:
        """Return string representation."""
        return f"ScrapeBadger(base_url={self._config.base_url!r})"
