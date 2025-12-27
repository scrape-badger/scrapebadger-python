"""ScrapeBadger Python SDK.

The official Python SDK for ScrapeBadger - async web scraping APIs
for Twitter and more.

Example:
    ```python
    import asyncio
    from scrapebadger import ScrapeBadger

    async def main():
        async with ScrapeBadger(api_key="your-api-key") as client:
            # Get a user profile
            user = await client.twitter.users.get_by_username("elonmusk")
            print(f"{user.name} has {user.followers_count:,} followers")

            # Search tweets
            tweets = await client.twitter.tweets.search("python programming")
            for tweet in tweets.data:
                print(f"@{tweet.username}: {tweet.text[:100]}...")

            # Iterate through all results
            async for tweet in client.twitter.tweets.search_all("python"):
                print(tweet.text)

    asyncio.run(main())
    ```

For more information, see https://docs.scrapebadger.com
"""

from scrapebadger._internal.config import ClientConfig
from scrapebadger._internal.exceptions import (
    AuthenticationError,
    InsufficientCreditsError,
    NotFoundError,
    RateLimitError,
    ScrapeBadgerError,
    ServerError,
    ValidationError,
)
from scrapebadger._internal.pagination import PaginatedResponse
from scrapebadger.client import ScrapeBadger

__version__ = "0.1.1"

__all__ = [
    "AuthenticationError",
    # Configuration
    "ClientConfig",
    "InsufficientCreditsError",
    "NotFoundError",
    # Pagination
    "PaginatedResponse",
    "RateLimitError",
    # Main client
    "ScrapeBadger",
    # Exceptions
    "ScrapeBadgerError",
    "ServerError",
    "ValidationError",
    # Version
    "__version__",
]
