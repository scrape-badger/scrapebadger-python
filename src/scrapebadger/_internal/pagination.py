"""Pagination utilities for the ScrapeBadger SDK."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Generic, TypeVar

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Callable

    from scrapebadger._internal.client import BaseClient

T = TypeVar("T")


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

    This function provides a convenient way to iterate through all pages
    of a paginated API endpoint without manually handling cursors.

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

        # Fetch page
        response = await client.get(path, params=request_params)

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

        # Check if we've reached the end
        if not cursor:
            break
