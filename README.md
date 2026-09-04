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

The official Python SDK for [ScrapeBadger](https://scrapebadger.com) - async web scraping APIs for Twitter, Google, Vinted, Reddit, and more.

## Features

- **Async-first** - Built with `asyncio` for high-performance concurrent scraping
- **Type-safe** - Full type hints and Pydantic models for all responses
- **Automatic pagination** - Iterator methods with smart rate limit handling
- **Resilient retries** - Exponential backoff on transient errors
- **37+ Twitter endpoints** - Tweets, users, lists, communities, trends, geo, real-time streams
- **19 Google product APIs** - Search (with optional deferred AI Overview follow-up), Maps, News, Hotels, Trends (incl. topic autocomplete), Jobs, Shopping (+ merchant URL enrichment), Patents, Scholar (search + profiles + author + author citation + cite formats), Images, Videos, Finance, AI Mode, Lens, **Local Pack**, **Shorts**, **Flights**, Products
- **Vinted scraping** - Search items, item details, user profiles, brands, colors, markets
- **Reddit scraping** - Search posts/subreddits/users/domains, subreddit posts, post comments, user profiles, trophies, wiki pages, moderators
- **Web scraping** - Anti-bot bypass, JS rendering, and AI data extraction

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

## Available APIs

| API | Description | Documentation |
|-----|-------------|---------------|
| **Web Scraping** | Scrape any website with JS rendering, anti-bot bypass, and AI extraction | [Web Scraping Guide](docs/web-scraping.md) |
| **Twitter** | 37+ endpoints for tweets, users, lists, communities, trends, and real-time streams | [Twitter Guide](docs/twitter.md) |
| **Google** | 19 products — Search, Maps, News, Hotels, Trends, Jobs, Shopping, Patents, Scholar, Images, Videos, Finance, AI Mode, Lens, Autocomplete, Local, Shorts, Flights, Products | [Google Guide](docs/google.md) |
| **Vinted** | Search items, item details, user profiles, brands, colors, statuses, and markets | [Vinted Guide](docs/vinted.md) |
| **Reddit** | Search posts, subreddits, users, and domains; fetch post comments, subreddit rules, moderators, wiki pages, user trophies | [Reddit Guide](docs/reddit.md) |
| **Instagram** | User profile/about/related/posts/videos/reels/tagged/pinned/followers/following/stories/highlights, media detail/comments/replies/likers/oEmbed, search (users/hashtags/places/top/reels/music/autocomplete), hashtag/location/audio feeds | [Instagram Guide](docs/instagram.md) |
| **Amazon** | 14 endpoints — search, autocomplete, product detail, offers, reviews, bestsellers, new releases, deals, category browse, seller profile/products/feedback, markets, categories | [Amazon Guide](docs/amazon.md) |
| **eBay** | 13 endpoints across 18 markets — search, search by image (visual search), completed/sold search, item detail, item reviews, seller profile/items/feedback, category browse, categories, autocomplete, markets | [eBay Guide](docs/ebay.md) |
| **YouTube** | 39 endpoints — search, autocomplete, video detail/related/comments/replies/transcript/captions/streams/live-chat/batch, channel detail + videos/shorts/streams/playlists/community/about/subscriber-count/in-channel-search/resolve, playlists/items/mixes, trending/hashtag/home, shorts, community post/comments, music search, oembed, categories/languages/regions | [YouTube Guide](docs/youtube.md) |
| **TikTok** | 25 endpoints — user profile/videos/followers/following/liked/reposts, video detail/comments/replies/related/transcript/oEmbed, search (general/videos/hashtags/users), music detail/videos, hashtag detail/videos, trending videos/hashtags/songs, ad library, regions | [TikTok Guide](docs/tiktok.md) |
| **Immobiliare** | 8 endpoints across immobiliare.it, indomio.es, indomio.gr, immotop.lu — autocomplete, search, listing detail, agency profile/listings, price stats, markets, reference | [Immobiliare Guide](docs/immobiliare.md) |
| **LoopNet** | 5 endpoints across loopnet.com/.ca/.co.uk/.fr/.es — commercial-real-estate search (for-lease/for-sale/auctions), listing detail, broker profile, markets, property types | [LoopNet Guide](docs/loopnet.md) |
| **Apartments.com** | US rental listings with UNIT-LEVEL pricing — search by location with bed/price filters, plus per-unit rent, beds, baths, sqft and availability for every rentable unit | [Apartments Guide](docs/apartments.md) |
| **Walmart** | 11 endpoints (US-only) — search, category browse, deals feed, autocomplete, product detail, reviews, seller profile/products, store detail, markets | [Walmart Guide](docs/walmart.md) |
| **Baidu** | 4 endpoints — web search (language + date filters), news vertical, image search, autocomplete. Results carry the **real target URL**, not just Baidu's tracking redirect | [Baidu Docs](https://docs.scrapebadger.com/baidu/overview) |
| **Bing** | 6 endpoints — web search (with ads + related searches), image search, video search, news vertical, autocomplete, markets | [Bing Docs](https://docs.scrapebadger.com/bing/overview) |
| **DuckDuckGo** | 7 endpoints — web search (with abstract box), image/news/video search, autocomplete, instant answers, regions | [DuckDuckGo Docs](https://docs.scrapebadger.com/duckduckgo/overview) |
| **Yahoo** | 6 endpoints across 35 markets — web search (with ads + related searches), image search, video search, news vertical, autocomplete, markets | [Yahoo Docs](https://docs.scrapebadger.com/yahoo/overview) |
| **Yandex** | 4 endpoints across 6 markets (tr/com/ru/by/kz/uz) — web search (organic + ads + sitelinks + inline media), image search, reverse-image (CBIR) search, markets | [Yandex Docs](https://docs.scrapebadger.com/yandex/overview) |
| **ChatGPT** | Prompt the real chatgpt.com anonymously — structured answer with citations anchored to character offsets, the full retrieved search trail, and AEO/GEO brand-visibility analysis | [ChatGPT Guide](docs/chatgpt.md) |
| **Gemini** | Prompt the real gemini.google.com anonymously — structured answer with cited web sources, the full retrieved search trail, and AEO/GEO brand-visibility analysis | [Gemini Docs](https://docs.scrapebadger.com/gemini/overview) |

## Error Handling

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
    retry_on_status=(500, 502, 503, 504),
    headers={"X-Custom-Header": "value"},
)

client = ScrapeBadger(config=config)
```

### Retry Behavior

The SDK automatically retries requests that fail with 500, 502, 503, or 504 status
codes, as well as transport-level failures (timeouts, network errors, dropped
connections), using exponential backoff (1s, 2s, 4s, 8s, ...). Each retry logs a
warning:

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

- **Documentation**: [docs.scrapebadger.com](https://docs.scrapebadger.com)
- **Issues**: [GitHub Issues](https://github.com/scrape-badger/scrapebadger-python/issues)
- **Email**: support@scrapebadger.com
- **Discord**: [Join our community](https://discord.com/invite/3WvwTyWVCx)

---

Made with ❤️ by [ScrapeBadger](https://scrapebadger.com)
