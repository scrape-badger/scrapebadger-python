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
- **Smart rate limit handling** - Reads API rate limit headers and automatically throttles pagination to avoid hitting limits
- **Resilient retries** - 10 automatic retries with exponential backoff on 502/503/504 errors, with console warnings on each retry
- **Comprehensive coverage** - Access to 37+ Twitter endpoints (tweets, users, lists, communities, trends, geo)
- **Web scraping API** - Scrape any website with anti-bot bypass, JS rendering, and AI data extraction

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

        # Scrape a website
        result = await client.web.scrape("https://scrapebadger.com", format="markdown")
        print(result.content)

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

### Web Scraping

#### Basic Scrape

```python
async with ScrapeBadger(api_key="your-key") as client:
    result = await client.web.scrape("https://scrapebadger.com", format="markdown")
    print(result.content)
    print(f"Credits used: {result.credits_used}")
```

#### JavaScript Rendering

```python
result = await client.web.scrape(
    "https://spa-website.com",
    render_js=True,
    wait_for="#dynamic-content",
    wait_timeout=10000,
)
```

#### Anti-Bot Bypass with Escalation

```python
result = await client.web.scrape(
    "https://protected-site.com",
    escalate=True,
    anti_bot=True,
    country="US",
    max_cost=20,
)
```

#### AI Data Extraction

```python
result = await client.web.extract(
    "https://scrapebadger.com/pricing",
    prompt="Extract all pricing plan names and prices as a JSON array",
    format="markdown",
)
print(result.ai_extraction)  # Structured data from LLM
```

#### Detect Anti-Bot Protection

```python
detection = await client.web.detect("https://protected-site.com")
for system in detection.antibot_systems:
    print(f"{system['system']}: confidence {system['confidence']}")
print(f"Recommendation: {detection.recommendation}")
```

#### Browser Automation

```python
result = await client.web.scrape(
    "https://scrapebadger.com",
    render_js=True,
    js_scenario=[
        {"type": "click", "selector": "#load-more"},
        {"type": "wait", "milliseconds": 2000},
        {"type": "scroll", "direction": "down", "amount": 1000},
    ],
)
```

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

### Twitter Streams (Real-Time Monitoring)

Monitor Twitter accounts in real-time with WebSocket delivery:

```python
import asyncio
from scrapebadger import ScrapeBadger

async def main():
    async with ScrapeBadger(api_key="your-key") as client:
        # Create a stream monitor
        monitor = await client.twitter.stream.create_monitor(
            name="Tech CEOs",
            usernames=["elonmusk", "sama", "naval"],
            poll_interval_seconds=5.0,
        )
        print(f"Monitor '{monitor.name}' created (tier: {monitor.pricing_tier})")
        print(f"Estimated cost: {monitor.estimated_credits_per_hour:.0f} credits/hour")

        # List monitors
        result = await client.twitter.stream.list_monitors(status="active")
        print(f"{result.total} active monitors")

        # Stream tweets via WebSocket
        async with client.twitter.stream.connect(reconnect=True) as events:
            async for event in events:
                if event.type == "tweet":
                    print(f"@{event.author_username}: {event.tweet.text}")
                    print(f"  Detected in {event.latency_ms}ms")
                elif event.type == "connected":
                    print(f"Connected (id: {event.connection_id})")

        # Pause/resume/delete
        await client.twitter.stream.pause_monitor(monitor.id)
        await client.twitter.stream.delete_monitor(monitor.id)

asyncio.run(main())
```

#### Webhook Verification

Verify incoming webhook signatures in your receiver:

```python
from scrapebadger.twitter.stream import verify_webhook_signature

@app.post("/webhook")
async def handle_webhook(request):
    signature = request.headers["x-scrapebadger-signature"]
    body = await request.body()
    if not verify_webhook_signature("your-secret", body, signature):
        return JSONResponse({"error": "Invalid signature"}, status_code=401)
    event = json.loads(body)
    # Process event...
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
    max_retries=5,      # Retry attempts (default: 10)
)
```

### Advanced Configuration

```python
from scrapebadger import ScrapeBadger
from scrapebadger._internal import ClientConfig

config = ClientConfig(
    api_key="your-key",
    base_url="https://scrapebadger.com",
    timeout=300.0,
    connect_timeout=10.0,
    max_retries=10,
    retry_on_status=(502, 503, 504),
    headers={"X-Custom-Header": "value"},
)

client = ScrapeBadger(config=config)
```

### Retry Behavior

The SDK automatically retries requests that fail with 502, 503, or 504 status codes
using exponential backoff (1s, 2s, 4s, 8s, ...). Each retry logs a warning:

```
⚠ 503 Service Unavailable — retrying in 4s (attempt 3/10)
```

To see these warnings, configure Python logging:

```python
import logging
logging.basicConfig(level=logging.WARNING)
```

### Rate Limit Aware Pagination

When using `*_all` pagination methods, the SDK reads `X-RateLimit-Remaining` and
`X-RateLimit-Reset` headers from each response. When remaining requests drop below
20% of your tier's limit, pagination automatically slows down to spread requests
across the remaining window — preventing 429 errors. A warning is logged when
throttling activates:

```
⚠ Rate limit: 25/300 remaining (resets in 42s), throttling pagination to ~0.6 req/s
```

This works transparently with all tier levels (Free: 60/min, Basic: 300/min,
Pro: 1000/min, Enterprise: 5000/min).

## API Reference

### Web Scraping Endpoints

| Method | Description |
|--------|-------------|
| `scrape` | Scrape a URL with optional JS rendering, anti-bot bypass, screenshots, video, and AI extraction |
| `extract` | Convenience wrapper — scrapes with AI extraction enabled |
| `detect` | Detect anti-bot and CAPTCHA systems on a URL |

### Web Scraping Response Models

- `ScrapeResult` - Full scrape response with content, metadata, blocking info, and AI extraction
- `DetectResult` - Protection detection results with system list and recommendation

### Twitter Endpoints

| Category | Methods |
|----------|---------|
| **Tweets** | `get_by_id`, `get_by_ids`, `search`, `search_all`, `get_user_tweets`, `get_user_tweets_all`, `get_replies`, `get_retweeters`, `get_favoriters`, `get_similar` |
| **Users** | `get_by_id`, `get_by_username`, `get_about`, `search`, `search_all`, `get_followers`, `get_followers_all`, `get_following`, `get_following_all`, `get_follower_ids`, `get_following_ids`, `get_latest_followers`, `get_latest_following`, `get_verified_followers`, `get_followers_you_know`, `get_subscriptions`, `get_highlights` |
| **Lists** | `get_detail`, `search`, `get_tweets`, `get_tweets_all`, `get_members`, `get_members_all`, `get_subscribers`, `get_my_lists` |
| **Communities** | `get_detail`, `search`, `get_tweets`, `get_tweets_all`, `get_members`, `get_moderators`, `search_tweets`, `get_timeline` |
| **Trends** | `get_trends`, `get_place_trends`, `get_available_locations` |
| **Geo** | `get_detail`, `search` |
| **Streams** | `create_monitor`, `list_monitors`, `get_monitor`, `update_monitor`, `pause_monitor`, `resume_monitor`, `delete_monitor`, `list_delivery_logs`, `list_billing_logs`, `connect` |

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
- `StreamMonitor` - Stream monitor configuration and status
- `StreamMonitorList` - Paginated list of monitors
- `TweetEvent` - Real-time tweet delivery event with latency
- `ConnectedEvent`, `PingEvent`, `ErrorEvent` - WebSocket lifecycle events
- `DeliveryLog`, `BillingLog` - Audit log records
- `ScrapeResult` - Web scrape result with content, blocking details, AI extraction
- `DetectResult` - Anti-bot/CAPTCHA detection result

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
