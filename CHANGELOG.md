# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.8.1] - 2026-05-28

### Removed

- **`client.reddit.subreddits.moderators(...)`** — Reddit gated the moderator listing behind authentication in 2024. There is no public path that yields the data. Removed the method along with `RedditModerator` and `SubredditModeratorResponse` types rather than ship a permanently-broken endpoint.

### Fixed

- `client.reddit.search.subreddits(...)` no longer crashes when Reddit returns banned/quarantined subreddits with `null` values for required-typed fields (previously raised a backend 500 / ValidationError).

## [0.8.0] - 2026-05-28

### Added

- **Reddit Scraper API** — new `client.reddit.*` namespace covering 22 endpoints across search, posts, subreddits, users, and wiki:
  - `client.reddit.search.posts(q, ...)` — global or subreddit-scoped post search with full Reddit syntax (title:, author:, subreddit:, flair:, AND/OR/NOT)
  - `client.reddit.search.subreddits(q, ...)`, `client.reddit.search.users(q, ...)`
  - `client.reddit.search.domain_posts(domain, ...)` — posts linking to an external domain
  - `client.reddit.posts.trending(...)`, `client.reddit.posts.get(post_id)`
  - `client.reddit.posts.comments(post_id, depth=...)` — full nested comment trees with configurable depth (0–10)
  - `client.reddit.posts.duplicates(post_id, ...)` — cross-post detection
  - `client.reddit.subreddits.get(name)`, `.posts(...)`, `.rules(...)`, `.moderators(...)`, `.wiki_pages(...)`, `.wiki_page(...)`, `.popular(...)`, `.new(...)`
  - `client.reddit.users.get(name)`, `.posts(...)`, `.comments(...)`, `.moderated(...)`, `.trophies(...)`
- **Comprehensive Reddit response models** — `RedditPost` (66 fields), `RedditComment` (34), `RedditSubreddit` (48), `RedditUser` (27)
- **Datetime parity** — every datetime field ships both Unix timestamp (`*_utc`) and ISO 8601 UTC string (`*_at`)
- Frozen Pydantic models with `extra="ignore"` for forward compatibility

## [0.7.0] - 2026-04-21

### Added

- **`client.google.shopping.product(product_id, ...)`** — Shopping product detail page fetch by `product_id`.
- **`client.google.shopping.click(title, source, q, product_id?)`** — Resolve the direct merchant URL for a Shopping product tile via Google's "I'm Feeling Lucky" redirect.
- **`client.google.search.light(q, ...)`** — Lightweight `mode=fast` SERP — organic results + related searches only, ~40% faster than the full SERP.
- **`client.google.search.search(..., mode="full" | "fast")`** — New `mode` parameter on the main search method. `mode="fast"` hits Google's lite `gbv=1` endpoint.
- **`client.google.maps.posts(..., next_page_token=...)`** — Pagination support on business posts.

### Changed

- **Removed hardcoded per-endpoint credit numbers from docstrings and docs.** Credit costs are configured per-endpoint by ScrapeBadger admins and returned live from `GET /public/pricing` — no more stale "costs 2 credits" comments that go out of sync when pricing changes.
- **`client.google.products.detail(product_id, q=None, ...)`** — `q` is now optional. The backend accepts lookups by `product_id` alone; pass `q` only when you want the richer `/async/oapv` context blob.
- CHANGELOG section heading for 0.6.0 renamed from "Google Scrapingdog parity" to "Google parity".

### Removed

- **`client.google.local`** — removed. The Local Pack is exposed via the SERP `/v1/google/search` response's `local_results` field rather than a dedicated endpoint. **Breaking** for anyone using the dedicated local client; migrate to reading `local_results` from `client.google.search.search(...)`.

## [0.6.0] - 2026-04-11

### Added — Google parity (refs scrape-badger/scrapebadger#135)

Three new Google product sub-clients and deeper Scholar / Trends / Search surface:

- **`client.google.local`** — Local Pack business listings ranked for a SERP query (`tbm=lcl`). Driven by `q + location/uule`, returns ratings, reviews, addresses, phone numbers, and GPS coordinates. Complementary to the Maps API.
- **`client.google.shorts`** — Short-form vertical video results (YouTube Shorts, TikTok, Facebook Reels) via Google's Shorts SERP mode (`udm=39`).
- **`client.google.flights`** — One-way, round-trip, and multi-city flight search with passenger config, cabin class, stops filter, and max-price. Returns `best_flights`, `other_flights`, `price_insights`, and per-offer carbon emissions.
- **`client.google.scholar.profiles(mauthors, ...)`** — Author profile search by name with `after_author` / `before_author` pagination.
- **`client.google.scholar.author(author_id, ...)`** — Full author profile (articles, citation stats, co-authors).
- **`client.google.scholar.author_citation(author_id, ...)`** — Citations-per-year chart for a Scholar author.
- **`client.google.scholar.cite(q, ...)`** — MLA / APA / Chicago / Harvard / Vancouver citation formats plus export links (BibTeX / RIS / EndNote / RefWorks).
- **`client.google.trends.autocomplete(q, ...)`** — Categorized Knowledge Graph topic entities (`mid`, `type`, link) for a query prefix. Distinct from Google Search autocomplete.
- **`client.google.search.search(..., ai_overview=True)`** — Optional flag that chases Google's deferred AI Overview `page_token` with a follow-up fetch and merges the result into `ai_overview`. Adds ~1s and 1 credit only when the SERP actually defers the overview.

The Google product roster is now **19** (was 16).

## [0.2.0] - 2026-03-05

### Added

- **Twitter Streams**: Real-time tweet monitoring via WebSocket and webhooks
  - `StreamClient` with full monitor CRUD: `create_monitor`, `list_monitors`, `get_monitor`, `update_monitor`, `pause_monitor`, `resume_monitor`, `delete_monitor`
  - WebSocket streaming via `connect()` async context manager with auto-reconnect support
  - `verify_webhook_signature()` utility for HMAC-SHA256 webhook verification
  - Delivery log and billing log listing: `list_delivery_logs`, `list_billing_logs`
  - Full type-safe models: `StreamMonitor`, `StreamMonitorList`, `TweetEvent`, `ConnectedEvent`, `PingEvent`, `ErrorEvent`, `DeliveryLog`, `BillingLog`
  - `WebSocketStreamError` exception for stream connection failures

## [0.1.1] - 2024-12-27

### Fixed

- Fixed Python 3.10 compatibility for StrEnum
- Fixed all ruff linting issues
- Fixed mypy type checking errors
- Fixed GitHub badge URLs to correct organization

## [0.1.0] - 2024-12-27

### Added

- Initial release of the ScrapeBadger Python SDK
- Full async support with `httpx`
- Strongly-typed responses using Pydantic v2
- Twitter API client with 37+ endpoints:
  - Tweets: get by ID, search, get replies, retweeters, favoriters
  - Users: get by username/ID, followers, following, search
  - Lists: get details, members, tweets, search
  - Communities: get details, members, moderators, tweets
  - Trends: get trends, place-specific trends, available locations
  - Geo: search places, get place details
- Automatic pagination with async iterators
- Built-in retry logic with exponential backoff
- Comprehensive exception handling
- Full type hints for IDE support

### Security

- API key authentication
- No sensitive data logged

[Unreleased]: https://github.com/scrape-badger/scrapebadger-python/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/scrape-badger/scrapebadger-python/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/scrape-badger/scrapebadger-python/releases/tag/v0.1.0
