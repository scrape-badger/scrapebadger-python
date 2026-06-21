"""Main ScrapeBadger client.

This module provides the main entry point for the ScrapeBadger SDK.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from scrapebadger._internal.client import BaseClient
from scrapebadger._internal.config import ClientConfig
from scrapebadger.amazon.client import AmazonClient
from scrapebadger.ebay.client import EbayClient
from scrapebadger.google.client import GoogleClient
from scrapebadger.reddit.client import RedditClient
from scrapebadger.tiktok.client import TikTokClient
from scrapebadger.twitter.client import TwitterClient
from scrapebadger.vinted.client import VintedClient
from scrapebadger.web.client import WebClient
from scrapebadger.youtube.client import YoutubeClient

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
        self._amazon: AmazonClient | None = None
        self._ebay: EbayClient | None = None
        self._youtube: YoutubeClient | None = None
        self._tiktok: TikTokClient | None = None

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
