"""Main ScrapeBadger client.

This module provides the main entry point for the ScrapeBadger SDK.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from scrapebadger._internal.client import BaseClient
from scrapebadger._internal.config import ClientConfig
from scrapebadger.twitter.client import TwitterClient

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

    @property
    def config(self) -> ClientConfig:
        """Get the client configuration."""
        return self._config

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
