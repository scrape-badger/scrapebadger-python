"""Pagination utilities for the ScrapeBadger SDK."""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Generic, TypeVar

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Callable

    from scrapebadger._internal.client import BaseClient

logger = logging.getLogger("scrapebadger")

T = TypeVar("T")

# Throttle pagination when remaining requests drop below this fraction of the limit.
_RATE_LIMIT_THRESHOLD = 0.20


@dataclass
class PaginatedResponse(Generic[T]):
    """A paginated response containing a page of data.

    This class represents a single page of results from a paginated API endpoint.
    Use the `next_cursor` to fetch subsequent pages, or use the `paginate()`
    async generator for automatic iteration.

    Attributes:
        data: List of items in this page.
        next_cursor: Cursor for fetching the next page, or None if this is the last page.
        has_more: Whether there are more pages available.

    Example:
        ```python
        # Manual pagination
        response = await client.twitter.users.get_followers("elonmusk")
        for user in response.data:
            print(user.username)

        if response.has_more:
            next_page = await client.twitter.users.get_followers(
                "elonmusk",
                cursor=response.next_cursor
            )
        ```
    """

    data: list[T]
    next_cursor: str | None = None

    @property
    def has_more(self) -> bool:
        """Check if there are more pages available."""
        return self.next_cursor is not None

    def __len__(self) -> int:
        """Return the number of items in this page."""
        return len(self.data)

    def __iter__(self) -> Any:
        """Iterate over items in this page."""
        return iter(self.data)

    def __bool__(self) -> bool:
        """Return True if there are items in this page."""
        return bool(self.data)


def _compute_throttle_delay(
    remaining: int,
    limit: int,
    reset_ts: int,
) -> float | None:
    """Return a sleep delay in seconds if rate-limit throttling is needed.

    Throttling kicks in when ``remaining < limit * _RATE_LIMIT_THRESHOLD``.
    The delay spreads remaining requests evenly across the time left in the
    current window, giving a minimum of 0.05 s.

    Args:
        remaining: Requests remaining in the current window.
        limit: Total requests allowed per window.
        reset_ts: Unix timestamp when the window resets.

    Returns:
        Seconds to sleep, or ``None`` if no throttling is needed.
    """
    if remaining >= limit * _RATE_LIMIT_THRESHOLD:
        return None

    seconds_left = max(reset_ts - time.time(), 1.0)
    # Spread remaining requests over the window — guard against zero division.
    if remaining <= 0:
        return seconds_left

    delay = seconds_left / remaining
    return max(delay, 0.05)


async def paginate(
    client: BaseClient,
    path: str,
    params: dict[str, Any],
    item_parser: Callable[[dict[str, Any]], T],
    *,
    max_pages: int | None = None,
    max_items: int | None = None,
) -> AsyncIterator[T]:
    """Async generator for automatic pagination through results.

    Reads ``X-RateLimit-Remaining``, ``X-RateLimit-Limit``, and
    ``X-RateLimit-Reset`` response headers on every page.  When remaining
    requests drop below 20 % of the limit a warning is logged and requests
    are spread out over the remaining window time via ``asyncio.sleep``.

    Args:
        client: The base HTTP client.
        path: API endpoint path.
        params: Query parameters (cursor will be added automatically).
        item_parser: Function to parse each item from raw dict to model.
        max_pages: Maximum number of pages to fetch. None for unlimited.
        max_items: Maximum number of items to yield. None for unlimited.

    Yields:
        Parsed items from each page.

    Example:
        ```python
        # Iterate through all followers
        async for user in paginate(
            client,
            "/v1/twitter/users/elonmusk/followers",
            {},
            User.model_validate,
            max_items=1000
        ):
            print(user.username)

        # Or collect into a list
        followers = [
            user async for user in paginate(
                client, path, {}, User.model_validate, max_pages=5
            )
        ]
        ```
    """
    cursor: str | None = None
    pages_fetched = 0
    items_yielded = 0

    while True:
        # Check page limit
        if max_pages is not None and pages_fetched >= max_pages:
            break

        # Add cursor to params if we have one
        request_params = {**params}
        if cursor:
            request_params["cursor"] = cursor

        # Fetch page — use get_with_headers so we can inspect rate-limit state.
        response, headers = await client.get_with_headers(path, params=request_params)

        # Parse and yield items
        data = response.get("data", [])
        if data is None:
            data = []

        for item in data:
            if max_items is not None and items_yielded >= max_items:
                return
            yield item_parser(item)
            items_yielded += 1

        # Update cursor for next page
        cursor = response.get("next_cursor")
        pages_fetched += 1

        # Check if we've reached the end before potentially sleeping.
        if not cursor:
            break

        # Rate-limit-aware throttling between pages.
        _maybe_throttle_between_pages(headers)
        delay = _extract_throttle_delay(headers)
        if delay is not None:
            await asyncio.sleep(delay)


def _extract_throttle_delay(headers: dict[str, str]) -> float | None:
    """Parse rate-limit headers and return a throttle delay if needed.

    Returns ``None`` when headers are absent or throttling is not required.
    """
    raw_remaining = headers.get("x-ratelimit-remaining") or headers.get(
        "X-RateLimit-Remaining"
    )
    raw_limit = headers.get("x-ratelimit-limit") or headers.get("X-RateLimit-Limit")
    raw_reset = headers.get("x-ratelimit-reset") or headers.get("X-RateLimit-Reset")

    if raw_remaining is None or raw_limit is None or raw_reset is None:
        return None

    try:
        remaining = int(raw_remaining)
        limit = int(raw_limit)
        reset_ts = int(raw_reset)
    except ValueError:
        return None

    return _compute_throttle_delay(remaining, limit, reset_ts)


def _maybe_throttle_between_pages(headers: dict[str, str]) -> None:
    """Log a warning if rate-limit throttling will be applied."""
    raw_remaining = headers.get("x-ratelimit-remaining") or headers.get(
        "X-RateLimit-Remaining"
    )
    raw_limit = headers.get("x-ratelimit-limit") or headers.get("X-RateLimit-Limit")
    raw_reset = headers.get("x-ratelimit-reset") or headers.get("X-RateLimit-Reset")

    if raw_remaining is None or raw_limit is None or raw_reset is None:
        return

    try:
        remaining = int(raw_remaining)
        limit = int(raw_limit)
        reset_ts = int(raw_reset)
    except ValueError:
        return

    delay = _compute_throttle_delay(remaining, limit, reset_ts)
    if delay is None:
        return

    resets_in = max(int(reset_ts - time.time()), 0)
    rate = round(1.0 / delay, 1) if delay > 0 else 0
    logger.warning(
        "Rate limit: %d/%d remaining (resets in %ds), throttling pagination to ~%s req/s",
        remaining,
        limit,
        resets_in,
        rate,
    )
