# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.23.0] - 2026-07-25

### Added

- **eBay `pagination.has_more`** — the stop signal for paging through completed/sold listings. `total_pages`/`total_results` are `None` on eBay's sold grid, and past the last page eBay re-serves that page instead of returning empty, so looping "until the results are empty" never terminated. Loop `while r.pagination.has_more` instead; the API now also returns an empty page once you page past the end. The `page` ceiling is raised to 1000 (a broad sold search runs ~133 pages deep at `per_page=240`, ~26k listings). (SCR-124)

### Changed

- **eBay `is_sponsored` is now `bool | None` and always `None`** — previously typed `bool` and reported `True` for 100% of results. eBay renders its "Sponsored" badge into every result card as anti-scraping bait, so promoted placements cannot be distinguished from organic ones in the response. The field reports `None` (unknown) rather than a value that was wrong on every row. (SCR-124)

## [0.22.0] - 2026-07-23

### Added

- **Google Flights `sort_by`** — `client.google.flights.search(..., sort_by="price")` now returns the FULL price-sorted inventory (every carrier, the cheap long-layover fares) plus Google's own price floor, typical range, and price history, instead of only the ~6-8 "best" preview. Default `sort_by="top"` keeps the fast best-picks behaviour. (SCR-123)

## [0.21.0] - 2026-07-17

### Added

- **eBay completed-search sold dates** — `SearchResult` now exposes `sold_date` (sale date text as rendered by eBay, e.g. "2 Jul 2026"; localized on non-English markets) and `sold_date_at` (best-effort ISO date "2026-07-02", `None` when the market's format isn't English) on `client.ebay` completed/sold result cards. (SCR-122)
- **eBay item `is_ended`** — `Item` now exposes `is_ended` (`True` when the listing has closed — sold or ended — any buying format, default `False`). `end_time_utc`/`end_time_at` broaden from auction-only to the listing end: auction close or sold time for ended listings of any format; still `None` for active fixed-price listings. (SCR-122)

## [0.20.0] - 2026-07-13

### Added

- **LinkedIn client** (`client.linkedin`) — LinkedIn's public, no-auth (logged-out) surface. Endpoints: `jobs_search()`, `get_job()`, `company_jobs()`, `get_company()`, `get_school()`, `get_profile()`, `get_post()`, `get_article()`, `get_course()`, `geo_suggest()`, `health()` under `/v1/linkedin`. Fully-typed Pydantic models (`LinkedInJobsSearchResponse`, `LinkedInJobDetail`, `LinkedInProfile` incl. nested experience/education, `LinkedInCompany`, `LinkedInSchool`, `LinkedInPost`, `LinkedInLearningCourse`, `LinkedInGeoSuggestResponse`). Sourced from the guest Jobs API and public SSR JSON-LD pages; deep logged-in data is auth-gated and out of scope. (SCR-119)

## [0.18.0] - 2026-07-12

### Added

- **Redfin client** (`client.redfin`) — Redfin (redfin.com, US) for-sale search, property detail, agent profiles, autocomplete, and markets. Endpoints: `search()`, `get_property()`, `get_agent()`, `autocomplete()`, `list_markets()`, mirroring the Immobiliare flat-client pattern, with fully-typed maximal-coverage Pydantic models (`RedfinSearchResponse`, `RedfinProperty` incl. nested `address`/`price_history`/`tax_history`/`schools`/`amenities`, `RedfinAgent`, etc.). Single market: redfin.com (US, USD, en-US). (SCR-116)

## [0.17.0] - 2026-07-08

### Added

- **LoopNet sub-client** (`client.loopnet`) — commercial-real-estate (CoStar) listings, brokers, and reference data across loopnet.com/.ca/.co.uk/.fr/.es (US/CA/UK/FR/ES). Endpoints: `search.search()` (for-lease / for-sale / auctions, all property types, filters, pagination), `listings.get()`, `brokers.get()`, `reference.markets()`, `reference.property_types()`, with fully-typed maximal-coverage Pydantic models (`LoopnetSearchResponse`, `LoopnetListingDetail` incl. offers/facts/brokers/media, `LoopnetBrokerProfile`, `LoopnetListingCard`, etc.). LoopNet is behind Akamai Bot Manager (browser-farm-only) — served via the ScrapeBadger farm. (SCR-102)

## [0.15.7] - 2026-07-07

### Added

- **Zillow sub-client** (`client.zillow`) — real-estate listings, property detail, and agent profiles from zillow.com (US + Canadian inventory). Five endpoints: `search.search()`, `search.autocomplete()`, `properties.get_property()`, `agents.get_agent()`, `reference.list_markets()`, with fully-typed maximal-coverage Pydantic models (`ZillowSearchResponse`, `ZillowProperty` incl. nested `home_facts`/`price_history`/`tax_history`/`schools`/`zestimate_history`, `ZillowAgent`, etc.). (SCR-99)

## [0.15.6] - 2026-07-07

### Added

- Add Leboncoin Scraper API client (France) — 10 endpoints: search, ad detail, similar ads, seller profile + listings, markets/regions/departments/categories/location search.

## [0.15.5] - 2026-07-02

### Added

- **Realtor sub-client** (`client.realtor`) — real-estate listings across realtor.com (US) and realtor.ca (Canada) behind a single `market` parameter. Four endpoints: `search.search()`, `search.autocomplete()`, `properties.get_property()`, `reference.list_markets()`, with fully-typed Pydantic models (`RealtorSearchResponse`, `RealtorPropertyDetail`, etc.). (SCR-98)

## [0.15.4] - 2026-06-30

### Added

- **`client.twitter.tweets.advanced_search()` / `advanced_search_all()`** — aliases for `search()` / `search_all()` that match the `/advanced_search` REST endpoint name, so the endpoint-named call no longer raises `AttributeError`. (SCR-52)

### Fixed

- **Auto-pagination no longer repeats the first page** (`*_all` iterators, e.g. `client.twitter.tweets.search_all`). The shared `paginate()` helper now stops when the backend returns the same cursor it was given, instead of re-fetching the page it just yielded — previously a non-advancing cursor from the API could cause a repeat-page loop. (SCR-52)

## [0.15.3] - 2026-06-30

### Added

- **Google Shopping offers by barcode** — `client.google.shopping.offers(barcode, *, gl=None, hl="en")` calls `GET /v1/google/shopping/offers`. Resolves a product barcode (GTIN-8/UPC-A/EAN-13/GTIN-14) to a product via Google web search, then returns its multi-seller Google Shopping prices (`barcode`, `resolved_query`, `product_title`, `offers`). Costs 14 credits; returns 422 for an invalid barcode and 404 if unresolvable.

## [0.15.2] - 2026-06-22

### Added

- **eBay auction data** on the eBay client models:
  - `SearchResult.current_bid` and `Item.current_bid` — an auction's current high bid (mirrors `price`).
  - `Item.end_time_utc` / `Item.end_time_at` — the absolute auction end time (Unix float / ISO-8601 Z).
  - `Item.buy_it_now_price` — the Buy It Now price for fixed-price listings, or an auction that also offers Buy It Now (`None` for pure auctions).
  - `bids` (bid count) and `time_left` (relative remaining, e.g. `"12h 16m"`) are now reliably populated for auction listings.

## [0.15.0] - 2026-06-21

### Added

- **eBay API client** (`client.ebay`) covering all 12 endpoints across 18 marketplaces:
  - `ebay.search.search()` — active-listing keyword search (category, condition, buying_format, price, free-shipping filters)
  - `ebay.search.completed()` — completed/sold listings (sold-price history)
  - `ebay.search.autocomplete()` — keyword suggestions
  - `ebay.items.get_item()` — full listing detail (images, shipping, item specifics, seller, returns)
  - `ebay.items.get_item_reviews()` — catalog product reviews + rating histogram (optional `product_id`)
  - `ebay.sellers.get_seller()` / `get_seller_items()` / `get_seller_feedback()`
  - `ebay.categories.browse_category()` — browse listings within a category
  - `ebay.reference.list_categories()` / `list_markets()`
- Frozen, forward-compatible Pydantic models for every eBay response field (exported with an `Ebay`-prefix at the top level, e.g. `EbayItem`, `EbaySearchResult`, `EbaySeller`, `EbayReview`, `EbayPrice`).

## [0.9.0] - 2026-05-29

### Changed (Breaking)

- **Reddit response models trimmed to fields available via old.reddit.com HTML/RSS** — after Reddit
  deprecated the unauthenticated `.json` API, the ScrapeBadger backend switched to scraping
  `old.reddit.com` HTML and RSS feeds. Fields that Reddit no longer exposes through that source have
  been removed from all models to keep the SDK types in sync with what the API actually returns.
  Consuming code that accessed removed fields will receive `AttributeError` at runtime.

  **`RedditPost`** — removed: `ups`, `downs`, `upvote_ratio`, `view_count`, `num_duplicates`,
  `edited`, `edited_at`, `is_video`, `is_locked`, `is_archived`, `is_pinned`,
  `is_robot_indexable`, `is_meta`, `is_crosspostable`, `send_replies`,
  `author_flair_text`, `author_flair_type`, `author_flair_template_id`,
  `link_flair_background_color`, `link_flair_text_color`, `link_flair_template_id`,
  `link_flair_type`, `link_flair_css_class`, `distinguished`, `thumbnail`,
  `thumbnail_width`, `thumbnail_height`, `post_hint`, `preview_images`, `media`,
  `gallery_data`, `crosspost_parent`, `suggested_sort`, `total_awards`, `awards`,
  `content_categories`, `removed_by_category`, `treatment_tags`, `subreddit_subscribers`.

  **`RedditComment`** — removed: `ups`, `downs`, `controversiality`, `edited`, `edited_at`,
  `gilded`, `is_locked`, `is_score_hidden`, `is_submitter`, `parent_id`, `post_title`,
  `send_replies`, `subreddit_type`, `total_awards`, `distinguished`,
  `author_flair_text`, `author_flair_type`.

  **`RedditSubreddit`** — removed: `subscribers`, `active_users`, `description_html`,
  `public_description_html`, `submit_text`, `submit_text_html`, `header_title`, `type`,
  `submission_type`, `is_quarantined`, `is_advertiser_friendly`, `advertiser_category`,
  `language`, `icon_url`, `header_url`, `banner_url`, `banner_background_color`,
  `primary_color`, `key_color`, `wiki_enabled`, `allow_images`, `allow_videos`,
  `allow_galleries`, `allow_polls`, `allow_discovery`, `spoilers_enabled`,
  `emojis_enabled`, `free_form_reports`, `accept_followers`, `restrict_posting`,
  `link_flair_enabled`, `link_flair_position`, `user_flair_enabled`,
  `user_flair_position`, `comment_score_hide_mins`, `should_archive_posts`,
  `allowed_media_in_comments`.

  **`RedditUser`** — removed: `id`, `fullname`, `description`, `icon_url`, `snoovatar_url`,
  `banner_url`, `profile_title`, `profile_url`, `awardee_karma`, `awarder_karma`,
  `has_verified_email`, `verified`, `accepts_followers`, `has_subscribed`, `is_employee`,
  `is_mod`, `is_suspended`, `is_nsfw`, `pref_show_snoovatar`.

  **`RedditRule`** — removed: `description_html`, `kind`, `violation_reason`.

- **Helper models deleted** — `RedditPreviewImage`, `RedditMedia`, `RedditAward`, and
  `RedditUserSummary` are no longer exported (they were only used by removed fields).
  Remove any imports of these names from consuming code.

### Added

- `RedditPagination` — new standalone pagination model (`after`, `before`, `count`, `limit`)
  exported from `scrapebadger.reddit`.

## [0.8.3] - 2026-05-29

### Fixed

- **Reddit search & listing methods sent the wrong query-parameter names**, causing a `422 'q' field required` against the live API. The API expects `q` (search query) and `t` (time filter); the SDK was sending `query` and `time_filter`. Fixed across `search.posts`, `search.subreddits`, `search.users`, `search.domain_posts`, `subreddits.posts`, `users.posts`, `users.comments`. The Python keyword arguments are unchanged (`query=`, `time_filter=`) — only the wire params are corrected.
- **`search.domain_posts()` hit the wrong URL** — `/v1/reddit/search/domain` with `domain` as a query param. The real route is `/v1/reddit/domains/{domain}/posts` (domain is a path segment). Fixed.

## [0.8.2] - 2026-05-29

### Fixed

- **`client.reddit.posts.get()` and `client.reddit.posts.comments()` were calling the wrong URL** — `/v1/reddit/posts/{subreddit}/{post_id}` (two path segments) instead of the actual API route `/v1/reddit/posts/{post_id}`. Both methods 404'd against the live API in 0.8.0/0.8.1. The `subreddit` positional argument has been **removed** from both methods — call `posts.get(post_id)` and `posts.comments(post_id, ...)`. This is a breaking change for anyone who worked around the bug, but the previous signature never worked against production.

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
