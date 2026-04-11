# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6.0] - 2026-04-11

### Added — Google Scrapingdog parity (refs scrape-badger/scrapebadger#135)

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
