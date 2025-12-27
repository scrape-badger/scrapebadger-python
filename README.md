<p align="center">
  <img src="https://scrapebadger.com/logo-dark.png" alt="ScrapeBadger" width="400">
</p>

<h1 align="center">ScrapeBadger Python SDK</h1>

<p align="center">
  <a href="https://pypi.org/project/scrapebadger/"><img src="https://img.shields.io/pypi/v/scrapebadger.svg" alt="PyPI version"></a>
  <a href="https://pypi.org/project/scrapebadger/"><img src="https://img.shields.io/pypi/pyversions/scrapebadger.svg" alt="Python versions"></a>
  <a href="https://github.com/scrape-badger/scrapebadger-python/blob/main/LICENSE"><img src="https://img.shields.io/pypi/l/scrapebadger.svg" alt="License"></a>
  <a href="https://github.com/scrape-badger/scrapebadger-python/actions/workflows/test.yml"><img src="https://github.com/scrape-badger/scrapebadger-python/actions/workflows/test.yml/badge.svg" alt="Tests"></a>
  <a href="https://codecov.io/gh/scrape-badger/scrapebadger-python"><img src="https://codecov.io/gh/scrape-badger/scrapebadger-python/branch/main/graph/badge.svg" alt="Coverage"></a>
  <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/badge/code%20style-ruff-000000.svg" alt="Code style: ruff"></a>
  <a href="https://mypy-lang.org/"><img src="https://img.shields.io/badge/type%20checked-mypy-blue.svg" alt="Type checked: mypy"></a>
</p>

The official Python SDK for [ScrapeBadger](https://scrapebadger.com) - async web scraping APIs for Twitter and more.

## Features

- **Async-first design** - Built with `asyncio` for high-performance concurrent scraping
- **Type-safe** - Full type hints and Pydantic models for all API responses
- **Automatic pagination** - Iterator methods for seamless pagination through large datasets
- **Retry logic** - Built-in exponential backoff for transient errors
- **Comprehensive coverage** - Access to 37+ Twitter endpoints (tweets, users, lists, communities, trends, geo)

## Installation

```bash
pip install scrapebadger
```

Or with [uv](https://github.com/astral-sh/uv):

```bash
uv add scrapebadger
```

## Quick Start

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

asyncio.run(main())
```

## Authentication

Get your API key from [scrapebadger.com](https://scrapebadger.com) and pass it to the client:

```python
from scrapebadger import ScrapeBadger

client = ScrapeBadger(api_key="sb_live_xxxxxxxxxxxxx")
```

You can also set the `SCRAPEBADGER_API_KEY` environment variable:

```bash
export SCRAPEBADGER_API_KEY="sb_live_xxxxxxxxxxxxx"
```

## Usage Examples

### Twitter Users

```python
async with ScrapeBadger(api_key="your-key") as client:
    # Get user by username
    user = await client.twitter.users.get_by_username("elonmusk")
    print(f"{user.name} (@{user.username})")
    print(f"Followers: {user.followers_count:,}")
    print(f"Following: {user.following_count:,}")
    print(f"Bio: {user.description}")

    # Get user by ID
    user = await client.twitter.users.get_by_id("44196397")

    # Get extended "About" information
    about = await client.twitter.users.get_about("elonmusk")
    print(f"Account based in: {about.account_based_in}")
    print(f"Username changes: {about.username_changes}")
```

### Twitter Tweets

```python
async with ScrapeBadger(api_key="your-key") as client:
    # Get a single tweet
    tweet = await client.twitter.tweets.get_by_id("1234567890")
    print(f"@{tweet.username}: {tweet.text}")
    print(f"Likes: {tweet.favorite_count:,}, Retweets: {tweet.retweet_count:,}")

    # Get multiple tweets
    tweets = await client.twitter.tweets.get_by_ids([
        "1234567890",
        "0987654321"
    ])

    # Search tweets
    from scrapebadger.twitter import QueryType

    results = await client.twitter.tweets.search(
        "python programming",
        query_type=QueryType.LATEST  # TOP, LATEST, or MEDIA
    )

    # Get user's timeline
    tweets = await client.twitter.tweets.get_user_tweets("elonmusk")
```

### Automatic Pagination

All paginated endpoints support both manual pagination and automatic iteration:

```python
async with ScrapeBadger(api_key="your-key") as client:
    # Manual pagination
    followers = await client.twitter.users.get_followers("elonmusk")
    for user in followers.data:
        print(f"@{user.username}")

    if followers.has_more:
        more = await client.twitter.users.get_followers(
            "elonmusk",
            cursor=followers.next_cursor
        )

    # Automatic pagination with async iterator
    async for follower in client.twitter.users.get_followers_all(
        "elonmusk",
        max_items=1000  # Optional limit
    ):
        print(f"@{follower.username}")

    # Collect all results into a list
    all_followers = [
        user async for user in client.twitter.users.get_followers_all(
            "elonmusk",
            max_pages=10
        )
    ]
```

### Twitter Lists

```python
async with ScrapeBadger(api_key="your-key") as client:
    # Search for lists
    lists = await client.twitter.lists.search("tech leaders")
    for lst in lists.data:
        print(f"{lst.name}: {lst.member_count} members")

    # Get list details
    lst = await client.twitter.lists.get_detail("123456")

    # Get list tweets
    tweets = await client.twitter.lists.get_tweets("123456")

    # Get list members
    members = await client.twitter.lists.get_members("123456")
```

### Twitter Communities

```python
async with ScrapeBadger(api_key="your-key") as client:
    from scrapebadger.twitter import CommunityTweetType

    # Search communities
    communities = await client.twitter.communities.search("python developers")

    # Get community details
    community = await client.twitter.communities.get_detail("123456")
    print(f"{community.name}: {community.member_count:,} members")
    print(f"Rules: {len(community.rules or [])}")

    # Get community tweets
    tweets = await client.twitter.communities.get_tweets(
        "123456",
        tweet_type=CommunityTweetType.LATEST
    )

    # Get members
    members = await client.twitter.communities.get_members("123456")
```

### Trending Topics

```python
async with ScrapeBadger(api_key="your-key") as client:
    from scrapebadger.twitter import TrendCategory

    # Get global trends
    trends = await client.twitter.trends.get_trends()
    for trend in trends.data:
        count = f"{trend.tweet_count:,}" if trend.tweet_count else "N/A"
        print(f"{trend.name}: {count} tweets")

    # Get trends by category
    news = await client.twitter.trends.get_trends(category=TrendCategory.NEWS)
    sports = await client.twitter.trends.get_trends(category=TrendCategory.SPORTS)

    # Get trends for a specific location (WOEID)
    us_trends = await client.twitter.trends.get_place_trends(23424977)  # US
    print(f"Trends in {us_trends.name}:")
    for trend in us_trends.trends:
        print(f"  - {trend.name}")

    # Get available trend locations
    locations = await client.twitter.trends.get_available_locations()
    us_cities = [loc for loc in locations.data if loc.country_code == "US"]
```

### Geographic Places

```python
async with ScrapeBadger(api_key="your-key") as client:
    # Search places by name
    places = await client.twitter.geo.search(query="San Francisco")
    for place in places.data:
        print(f"{place.full_name} ({place.place_type})")

    # Search by coordinates
    places = await client.twitter.geo.search(
        lat=37.7749,
        long=-122.4194,
        granularity="city"
    )

    # Get place details
    place = await client.twitter.geo.get_detail("5a110d312052166f")
```

## Error Handling

The SDK provides specific exception types for different error scenarios:

```python
from scrapebadger import (
    ScrapeBadger,
    ScrapeBadgerError,
    AuthenticationError,
    RateLimitError,
    InsufficientCreditsError,
    NotFoundError,
    ValidationError,
    ServerError,
)

async with ScrapeBadger(api_key="your-key") as client:
    try:
        user = await client.twitter.users.get_by_username("elonmusk")
    except AuthenticationError:
        print("Invalid API key")
    except RateLimitError as e:
        print(f"Rate limited. Retry after {e.retry_after} seconds")
        print(f"Limit: {e.limit}, Remaining: {e.remaining}")
    except InsufficientCreditsError:
        print("Out of credits! Purchase more at scrapebadger.com")
    except NotFoundError:
        print("User not found")
    except ValidationError as e:
        print(f"Invalid parameters: {e}")
    except ServerError:
        print("Server error, try again later")
    except ScrapeBadgerError as e:
        print(f"API error: {e}")
```

## Configuration

### Custom Timeout and Retries

```python
from scrapebadger import ScrapeBadger

client = ScrapeBadger(
    api_key="your-key",
    timeout=120.0,      # Request timeout in seconds (default: 300)
    max_retries=5,      # Retry attempts (default: 3)
)
```

### Advanced Configuration

```python
from scrapebadger import ScrapeBadger
from scrapebadger._internal import ClientConfig

config = ClientConfig(
    api_key="your-key",
    base_url="https://api.scrapebadger.com",
    timeout=300.0,
    connect_timeout=10.0,
    max_retries=3,
    retry_on_status=(502, 503, 504),
    headers={"X-Custom-Header": "value"},
)

client = ScrapeBadger(config=config)
```

## API Reference

### Twitter Endpoints

| Category | Methods |
|----------|---------|
| **Tweets** | `get_by_id`, `get_by_ids`, `search`, `search_all`, `get_user_tweets`, `get_user_tweets_all`, `get_replies`, `get_retweeters`, `get_favoriters`, `get_similar` |
| **Users** | `get_by_id`, `get_by_username`, `get_about`, `search`, `search_all`, `get_followers`, `get_followers_all`, `get_following`, `get_following_all`, `get_follower_ids`, `get_following_ids`, `get_latest_followers`, `get_latest_following`, `get_verified_followers`, `get_followers_you_know`, `get_subscriptions`, `get_highlights` |
| **Lists** | `get_detail`, `search`, `get_tweets`, `get_tweets_all`, `get_members`, `get_members_all`, `get_subscribers`, `get_my_lists` |
| **Communities** | `get_detail`, `search`, `get_tweets`, `get_tweets_all`, `get_members`, `get_moderators`, `search_tweets`, `get_timeline` |
| **Trends** | `get_trends`, `get_place_trends`, `get_available_locations` |
| **Geo** | `get_detail`, `search` |

### Response Models

All responses use strongly-typed Pydantic models:

- `Tweet` - Tweet data with text, metrics, media, polls, etc.
- `User` - User profile with bio, metrics, verification status
- `UserAbout` - Extended user information
- `List` - Twitter list details
- `Community` - Community with rules and admin info
- `Trend` - Trending topic
- `Place` - Geographic place
- `PaginatedResponse[T]` - Wrapper for paginated results

See the [full API documentation](https://scrapebadger.com/docs) for complete details.

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/scrape-badger/scrapebadger-python.git
cd scrapebadger-python

# Install dependencies with uv
uv sync --dev

# Install pre-commit hooks
uv run pre-commit install
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/scrapebadger --cov-report=html

# Run specific tests
uv run pytest tests/test_client.py -v
```

### Code Quality

```bash
# Lint
uv run ruff check src/ tests/

# Format
uv run ruff format src/ tests/

# Type check
uv run mypy src/

# All checks
uv run ruff check src/ tests/ && uv run ruff format --check src/ tests/ && uv run mypy src/
```

## Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting (`uv run pytest && uv run ruff check`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [scrapebadger.com/docs](https://scrapebadger.com/docs)
- **Issues**: [GitHub Issues](https://github.com/scrape-badger/scrapebadger-python/issues)
- **Email**: support@scrapebadger.com
- **Discord**: [Join our community](https://discord.gg/scrapebadger)

---

Made with ❤️ by [ScrapeBadger](https://scrapebadger.com)
