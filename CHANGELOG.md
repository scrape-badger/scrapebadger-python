# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
