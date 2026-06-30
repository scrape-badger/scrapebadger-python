"""Tests for pagination with rate-limit-aware throttling."""

from __future__ import annotations

import logging
import time
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from scrapebadger._internal.client import BaseClient
from scrapebadger._internal.config import ClientConfig
from scrapebadger._internal.pagination import paginate


@pytest.fixture
def config() -> ClientConfig:
    return ClientConfig(api_key="test_key", max_retries=1)


@pytest.fixture
def base_client(config: ClientConfig) -> BaseClient:
    return BaseClient(config)


def _make_page(
    items: list[dict[str, Any]],
    next_cursor: str | None = None,
    *,
    remaining: int = 300,
    limit: int = 300,
    reset_at: int | None = None,
) -> tuple[dict[str, Any], dict[str, str]]:
    reset_ts = reset_at if reset_at is not None else int(time.time()) + 60
    data: dict[str, Any] = {"data": items}
    if next_cursor:
        data["next_cursor"] = next_cursor
    headers = {
        "X-RateLimit-Remaining": str(remaining),
        "X-RateLimit-Limit": str(limit),
        "X-RateLimit-Reset": str(reset_ts),
    }
    return data, headers


class TestPaginateBasic:
    """Tests for basic pagination behaviour (no throttling)."""

    async def test_single_page_no_cursor(self, base_client: BaseClient) -> None:
        """Yields all items from a single page when there is no next_cursor."""
        page, headers = _make_page([{"id": "1"}, {"id": "2"}])
        base_client.get_with_headers = AsyncMock(return_value=(page, headers))  # type: ignore[method-assign]

        results = [item async for item in paginate(base_client, "/v1/test", {}, lambda x: x)]

        assert results == [{"id": "1"}, {"id": "2"}]
        assert base_client.get_with_headers.call_count == 1

    async def test_multiple_pages_follow_cursor(self, base_client: BaseClient) -> None:
        """Follows next_cursor across multiple pages."""
        page1, h1 = _make_page([{"id": "1"}], next_cursor="cur1")
        page2, h2 = _make_page([{"id": "2"}], next_cursor="cur2")
        page3, h3 = _make_page([{"id": "3"}])

        base_client.get_with_headers = AsyncMock(  # type: ignore[method-assign]
            side_effect=[(page1, h1), (page2, h2), (page3, h3)]
        )

        results = [item async for item in paginate(base_client, "/v1/test", {}, lambda x: x)]

        assert results == [{"id": "1"}, {"id": "2"}, {"id": "3"}]
        # second call must include cursor=cur1
        _, kwargs = base_client.get_with_headers.call_args_list[1]
        assert kwargs["params"]["cursor"] == "cur1"

    async def test_max_pages_limits_fetching(self, base_client: BaseClient) -> None:
        """Stops after max_pages regardless of next_cursor."""
        page, headers = _make_page([{"id": "1"}], next_cursor="cur")
        base_client.get_with_headers = AsyncMock(return_value=(page, headers))  # type: ignore[method-assign]

        results = [
            item async for item in paginate(base_client, "/v1/test", {}, lambda x: x, max_pages=2)
        ]

        assert len(results) == 2
        assert base_client.get_with_headers.call_count == 2

    async def test_max_items_limits_yielding(self, base_client: BaseClient) -> None:
        """Stops yielding once max_items is reached."""
        page1, h1 = _make_page([{"id": "1"}, {"id": "2"}, {"id": "3"}], next_cursor="c")
        page2, h2 = _make_page([{"id": "4"}])
        base_client.get_with_headers = AsyncMock(  # type: ignore[method-assign]
            side_effect=[(page1, h1), (page2, h2)]
        )

        results = [
            item async for item in paginate(base_client, "/v1/test", {}, lambda x: x, max_items=2)
        ]

        assert len(results) == 2
        assert results == [{"id": "1"}, {"id": "2"}]

    async def test_empty_data_field_stops_iteration(self, base_client: BaseClient) -> None:
        """Treats empty data list as last page."""
        page, headers = _make_page([], next_cursor="ghost")
        base_client.get_with_headers = AsyncMock(return_value=(page, headers))  # type: ignore[method-assign]

        results = [item async for item in paginate(base_client, "/v1/test", {}, lambda x: x)]

        assert results == []

    async def test_echoed_cursor_stops_iteration(self, base_client: BaseClient) -> None:
        """Stops when the backend echoes the same cursor it was given (SCR-52).

        A non-advancing cursor would otherwise re-fetch the page just yielded,
        causing the 'repeats first page' loop. Only two pages are mocked, so a
        third call would raise StopIteration and fail this test.
        """
        page1, h1 = _make_page([{"id": "1"}], next_cursor="c")
        page2, h2 = _make_page([{"id": "2"}], next_cursor="c")  # echoes "c"
        base_client.get_with_headers = AsyncMock(  # type: ignore[method-assign]
            side_effect=[(page1, h1), (page2, h2)]
        )

        results = [item async for item in paginate(base_client, "/v1/test", {}, lambda x: x)]

        assert results == [{"id": "1"}, {"id": "2"}]
        assert base_client.get_with_headers.call_count == 2

    async def test_item_parser_is_applied(self, base_client: BaseClient) -> None:
        """Applies item_parser to each raw dict."""
        page, headers = _make_page([{"value": 1}, {"value": 2}])
        base_client.get_with_headers = AsyncMock(return_value=(page, headers))  # type: ignore[method-assign]

        results = [
            item async for item in paginate(base_client, "/v1/test", {}, lambda x: x["value"] * 10)
        ]

        assert results == [10, 20]


class TestPaginateRateLimitThrottling:
    """Tests for rate-limit-aware throttling behaviour."""

    async def test_no_sleep_when_remaining_above_threshold(self, base_client: BaseClient) -> None:
        """Does NOT sleep when remaining is above 20% of limit."""
        # 100/300 = 33% > 20% — should not throttle
        page, headers = _make_page([{"id": "1"}], next_cursor=None, remaining=100, limit=300)
        base_client.get_with_headers = AsyncMock(return_value=(page, headers))  # type: ignore[method-assign]

        with patch("scrapebadger._internal.pagination.asyncio.sleep") as mock_sleep:
            results = [item async for item in paginate(base_client, "/v1/test", {}, lambda x: x)]

        assert results == [{"id": "1"}]
        mock_sleep.assert_not_called()

    async def test_sleep_when_remaining_below_20_percent(self, base_client: BaseClient) -> None:
        """Sleeps between pages when remaining drops below 20% of limit."""
        reset_ts = int(time.time()) + 60

        # Page 1 triggers throttle (remaining=10, limit=300 → 3.3% < 20%)
        page1, h1 = _make_page(
            [{"id": "1"}], next_cursor="c", remaining=10, limit=300, reset_at=reset_ts
        )
        page2, h2 = _make_page([{"id": "2"}], remaining=5, limit=300, reset_at=reset_ts)
        base_client.get_with_headers = AsyncMock(  # type: ignore[method-assign]
            side_effect=[(page1, h1), (page2, h2)]
        )

        with patch("scrapebadger._internal.pagination.asyncio.sleep") as mock_sleep:
            results = [item async for item in paginate(base_client, "/v1/test", {}, lambda x: x)]

        assert results == [{"id": "1"}, {"id": "2"}]
        # sleep must be called at least once
        assert mock_sleep.call_count >= 1
        # delay must be positive
        delay_arg = mock_sleep.call_args_list[0][0][0]
        assert delay_arg > 0

    async def test_warning_logged_when_throttling(
        self, base_client: BaseClient, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Emits a warning log through the 'scrapebadger' logger when throttling."""
        reset_ts = int(time.time()) + 60
        page1, h1 = _make_page(
            [{"id": "1"}], next_cursor="c", remaining=5, limit=300, reset_at=reset_ts
        )
        page2, h2 = _make_page([{"id": "2"}], remaining=5, limit=300, reset_at=reset_ts)
        base_client.get_with_headers = AsyncMock(  # type: ignore[method-assign]
            side_effect=[(page1, h1), (page2, h2)]
        )

        with (
            patch("scrapebadger._internal.pagination.asyncio.sleep"),
            caplog.at_level(logging.WARNING, logger="scrapebadger"),
        ):
            results = [item async for item in paginate(base_client, "/v1/test", {}, lambda x: x)]

        assert results == [{"id": "1"}, {"id": "2"}]
        assert any("throttling" in record.message.lower() for record in caplog.records)
        assert any(record.name == "scrapebadger" for record in caplog.records)

    async def test_warning_message_contains_rate_limit_info(
        self, base_client: BaseClient, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Warning message includes remaining/limit and resets-in info."""
        reset_ts = int(time.time()) + 45
        page1, h1 = _make_page(
            [{"id": "1"}], next_cursor="c", remaining=12, limit=300, reset_at=reset_ts
        )
        page2, h2 = _make_page([{"id": "2"}], remaining=12, limit=300, reset_at=reset_ts)
        base_client.get_with_headers = AsyncMock(  # type: ignore[method-assign]
            side_effect=[(page1, h1), (page2, h2)]
        )

        with (
            patch("scrapebadger._internal.pagination.asyncio.sleep"),
            caplog.at_level(logging.WARNING, logger="scrapebadger"),
        ):
            [item async for item in paginate(base_client, "/v1/test", {}, lambda x: x)]

        warning_msgs = [r.message for r in caplog.records if r.levelno == logging.WARNING]
        assert warning_msgs, "Expected at least one WARNING log"
        msg = warning_msgs[0]
        assert "12/300" in msg  # remaining/limit

    async def test_missing_rate_limit_headers_no_throttle(self, base_client: BaseClient) -> None:
        """Gracefully handles responses with no rate-limit headers (no sleep)."""
        page: dict[str, Any] = {"data": [{"id": "1"}]}
        headers: dict[str, str] = {}  # no rate limit headers
        base_client.get_with_headers = AsyncMock(return_value=(page, headers))  # type: ignore[method-assign]

        with patch("scrapebadger._internal.pagination.asyncio.sleep") as mock_sleep:
            results = [item async for item in paginate(base_client, "/v1/test", {}, lambda x: x)]

        assert results == [{"id": "1"}]
        mock_sleep.assert_not_called()

    async def test_exactly_at_threshold_no_throttle(self, base_client: BaseClient) -> None:
        """Does not throttle when remaining equals exactly 20% of limit."""
        # 60/300 = 20% — boundary, should NOT throttle (strictly below 20%)
        page, headers = _make_page([{"id": "1"}], remaining=60, limit=300)
        base_client.get_with_headers = AsyncMock(return_value=(page, headers))  # type: ignore[method-assign]

        with patch("scrapebadger._internal.pagination.asyncio.sleep") as mock_sleep:
            results = [item async for item in paginate(base_client, "/v1/test", {}, lambda x: x)]

        assert results == [{"id": "1"}]
        mock_sleep.assert_not_called()

    async def test_one_below_threshold_throttles(self, base_client: BaseClient) -> None:
        """Throttles when remaining is one below 20% of limit."""
        reset_ts = int(time.time()) + 60
        page1, h1 = _make_page(
            [{"id": "1"}], next_cursor="c", remaining=59, limit=300, reset_at=reset_ts
        )
        page2, h2 = _make_page([{"id": "2"}], remaining=59, limit=300, reset_at=reset_ts)
        base_client.get_with_headers = AsyncMock(  # type: ignore[method-assign]
            side_effect=[(page1, h1), (page2, h2)]
        )

        with patch("scrapebadger._internal.pagination.asyncio.sleep") as mock_sleep:
            [item async for item in paginate(base_client, "/v1/test", {}, lambda x: x)]

        assert mock_sleep.call_count >= 1
