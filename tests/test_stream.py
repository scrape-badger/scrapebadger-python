"""Unit tests for Twitter Streams StreamClient, models, and WebSocket streaming.

Tests are organized into:
- TestStreamModels: Pydantic model construction and validation
- TestStreamClient: Monitor CRUD HTTP methods
- TestStreamClientLogs: Delivery and billing log methods
- TestWebSocketUrl: _ws_url_from_base utility
- TestParseEvent: _parse_event dispatch logic
- TestConnectContextManager: WebSocket connect() behaviour (mocked)
- TestWebSocketStreamError: Exception attributes
"""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from scrapebadger._internal.exceptions import WebSocketStreamError
from scrapebadger.twitter.stream import (
    StreamClient,
    _parse_event,
    _ws_url_from_base,
    verify_webhook_signature,
)
from scrapebadger.twitter.stream_models import (
    BillingLog,
    BillingLogList,
    ConnectedEvent,
    DeliveryLog,
    DeliveryLogList,
    ErrorEvent,
    MonitorStatus,
    PingEvent,
    StreamEventType,
    StreamMonitor,
    StreamMonitorList,
    StreamTweet,
    TweetEvent,
)

# ---------------------------------------------------------------------------
# Shared sample data
# ---------------------------------------------------------------------------

MONITOR_RESPONSE: dict[str, Any] = {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "name": "Test Monitor",
    "usernames": ["elonmusk", "naval"],
    "poll_interval_seconds": 5.0,
    "status": "active",
    "status_reason": None,
    "webhook_url": "https://example.com/hook",
    "webhook_secret_set": True,
    "estimated_credits_per_hour": 1440.0,
    "pricing_tier": "Ultra",
    "created_at": "2026-03-03T10:00:00+00:00",
    "updated_at": "2026-03-03T10:00:00+00:00",
}

MONITOR_LIST_RESPONSE: dict[str, Any] = {
    "monitors": [MONITOR_RESPONSE],
    "total": 1,
    "page": 1,
    "page_size": 20,
}

DELIVERY_LOG_RESPONSE: dict[str, Any] = {
    "id": "aaaa-bbbb-cccc",
    "monitor_id": "550e8400-e29b-41d4-a716-446655440001",
    "monitor_name": "Test Monitor",
    "tweet_id": "1895234567890123456",
    "author_username": "elonmusk",
    "tweet_text_preview": "Tweet content here...",
    "tweet_url": "https://twitter.com/elonmusk/status/1895234567890123456",
    "tweet_published_at": "2026-03-03T09:59:57+00:00",
    "detected_at": "2026-03-03T10:00:00+00:00",
    "latency_ms": 3333,
    "latency_badge": "green",
    "delivery_status": "websocket_delivered",
    "webhook_status_code": None,
    "webhook_attempts": 0,
}

BILLING_LOG_RESPONSE: dict[str, Any] = {
    "id": "dddd-eeee-ffff",
    "monitor_id": "550e8400-e29b-41d4-a716-446655440001",
    "monitor_name": "Test Monitor",
    "billed_at": "2026-03-03T10:00:00+00:00",
    "num_accounts": 2,
    "credits_deducted": 4.0,
    "tier_label": "Ultra",
    "rate_applied": 2.0,
}

TWEET_EVENT_RAW: dict[str, Any] = {
    "type": "tweet",
    "monitor_id": "550e8400-e29b-41d4-a716-446655440001",
    "tweet_id": "1895234567890123456",
    "author_username": "elonmusk",
    "tweet_published_at": "2026-03-03T09:59:57.123000+00:00",
    "detected_at": "2026-03-03T10:00:00.456000+00:00",
    "latency_ms": 3333,
    "tweet": {
        "id": "1895234567890123456",
        "text": "Tweet content here...",
        "created_at": "Mon Mar 03 09:59:57 +0000 2026",
        "user_id": "44196397",
        "username": "elonmusk",
        "user_name": "Elon Musk",
        "favorite_count": 0,
        "retweet_count": 0,
        "reply_count": 0,
        "media": [],
        "urls": [],
        "hashtags": [],
    },
}

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_base_client() -> MagicMock:
    """Return a mock BaseClient with AsyncMock methods."""
    client = MagicMock()
    client.get = AsyncMock()
    client.post = AsyncMock()
    client._request = AsyncMock()
    client.config.api_key = "test_api_key_12345"
    client.config.base_url = "https://api.test.scrapebadger.com"
    return client


@pytest.fixture
def stream_client(mock_base_client: MagicMock) -> StreamClient:
    """Return a StreamClient backed by a mock base client."""
    return StreamClient(mock_base_client)


# ===========================================================================
# TestStreamModels
# ===========================================================================


class TestStreamModels:
    """Pydantic model construction and validation tests."""

    def test_stream_monitor_validates_active_status(self) -> None:
        monitor = StreamMonitor.model_validate(MONITOR_RESPONSE)
        assert monitor.id == "550e8400-e29b-41d4-a716-446655440001"
        assert monitor.name == "Test Monitor"
        assert monitor.usernames == ["elonmusk", "naval"]
        assert monitor.poll_interval_seconds == 5.0
        assert monitor.status == MonitorStatus.ACTIVE
        assert monitor.webhook_secret_set is True
        assert monitor.estimated_credits_per_hour == 1440.0
        assert monitor.pricing_tier == "Ultra"

    def test_stream_monitor_paused_status(self) -> None:
        data = {**MONITOR_RESPONSE, "status": "paused", "status_reason": "Low balance"}
        monitor = StreamMonitor.model_validate(data)
        assert monitor.status == MonitorStatus.PAUSED
        assert monitor.status_reason == "Low balance"

    def test_stream_monitor_error_status(self) -> None:
        data = {**MONITOR_RESPONSE, "status": "error"}
        monitor = StreamMonitor.model_validate(data)
        assert monitor.status == MonitorStatus.ERROR

    def test_stream_monitor_is_frozen(self) -> None:
        monitor = StreamMonitor.model_validate(MONITOR_RESPONSE)
        with pytest.raises(Exception):  # noqa: B017 - pydantic raises ValidationError or TypeError
            monitor.name = "mutated"  # type: ignore[misc]

    def test_stream_monitor_list_validates(self) -> None:
        result = StreamMonitorList.model_validate(MONITOR_LIST_RESPONSE)
        assert result.total == 1
        assert result.page == 1
        assert result.page_size == 20
        assert len(result.monitors) == 1
        assert result.monitors[0].name == "Test Monitor"

    def test_stream_monitor_list_empty_monitors(self) -> None:
        result = StreamMonitorList.model_validate(
            {"monitors": [], "total": 0, "page": 1, "page_size": 20}
        )
        assert result.total == 0
        assert result.monitors == []

    def test_stream_tweet_validates(self) -> None:
        tweet = StreamTweet.model_validate(TWEET_EVENT_RAW["tweet"])
        assert tweet.id == "1895234567890123456"
        assert tweet.text == "Tweet content here..."
        assert tweet.username == "elonmusk"
        assert tweet.favorite_count == 0
        assert tweet.media == []
        assert tweet.urls == []
        assert tweet.hashtags == []

    def test_tweet_event_validates(self) -> None:
        event = TweetEvent.model_validate(TWEET_EVENT_RAW)
        assert event.type == StreamEventType.TWEET
        assert event.monitor_id == "550e8400-e29b-41d4-a716-446655440001"
        assert event.tweet_id == "1895234567890123456"
        assert event.author_username == "elonmusk"
        assert event.latency_ms == 3333
        assert isinstance(event.tweet, StreamTweet)
        assert event.tweet.text == "Tweet content here..."

    def test_connected_event_validates(self) -> None:
        raw = {
            "type": "connected",
            "connection_id": "550e8400-e29b-41d4-a716-000000000000",
            "api_key_id": "ak_xxxxxxxx",
        }
        event = ConnectedEvent.model_validate(raw)
        assert event.type == StreamEventType.CONNECTED
        assert event.connection_id == "550e8400-e29b-41d4-a716-000000000000"
        assert event.api_key_id == "ak_xxxxxxxx"

    def test_ping_event_validates(self) -> None:
        raw = {"type": "ping", "timestamp": "2026-03-03T10:00:00.000000+00:00"}
        event = PingEvent.model_validate(raw)
        assert event.type == StreamEventType.PING
        assert event.timestamp == "2026-03-03T10:00:00.000000+00:00"

    def test_error_event_validates(self) -> None:
        raw = {"type": "error", "code": 4001, "message": "Invalid or missing API key"}
        event = ErrorEvent.model_validate(raw)
        assert event.type == StreamEventType.ERROR
        assert event.code == 4001
        assert event.message == "Invalid or missing API key"

    def test_delivery_log_validates(self) -> None:
        log = DeliveryLog.model_validate(DELIVERY_LOG_RESPONSE)
        assert log.id == "aaaa-bbbb-cccc"
        assert log.monitor_name == "Test Monitor"
        assert log.latency_ms == 3333
        assert log.latency_badge == "green"
        assert log.delivery_status == "websocket_delivered"
        assert log.webhook_status_code is None
        assert log.webhook_attempts == 0

    def test_delivery_log_list_validates(self) -> None:
        result = DeliveryLogList.model_validate(
            {"logs": [DELIVERY_LOG_RESPONSE], "total": 1, "page": 1, "page_size": 20}
        )
        assert result.total == 1
        assert len(result.logs) == 1

    def test_billing_log_validates(self) -> None:
        log = BillingLog.model_validate(BILLING_LOG_RESPONSE)
        assert log.id == "dddd-eeee-ffff"
        assert log.credits_deducted == 4.0
        assert log.num_accounts == 2
        assert log.tier_label == "Ultra"
        assert log.rate_applied == 2.0

    def test_billing_log_list_validates(self) -> None:
        result = BillingLogList.model_validate(
            {"logs": [BILLING_LOG_RESPONSE], "total": 1, "page": 1, "page_size": 20}
        )
        assert result.total == 1
        assert len(result.logs) == 1

    def test_monitor_status_values(self) -> None:
        assert MonitorStatus.ACTIVE == "active"
        assert MonitorStatus.PAUSED == "paused"
        assert MonitorStatus.ERROR == "error"

    def test_stream_event_type_values(self) -> None:
        assert StreamEventType.CONNECTED == "connected"
        assert StreamEventType.PING == "ping"
        assert StreamEventType.TWEET == "tweet"
        assert StreamEventType.ERROR == "error"


# ===========================================================================
# TestWebSocketUrl
# ===========================================================================


class TestWebSocketUrl:
    """Tests for the _ws_url_from_base utility."""

    def test_https_becomes_wss(self) -> None:
        url = _ws_url_from_base("https://scrapebadger.com")
        assert url == "wss://scrapebadger.com/v1/twitter/stream"

    def test_http_becomes_ws(self) -> None:
        url = _ws_url_from_base("http://localhost:8000")
        assert url == "ws://localhost:8000/v1/twitter/stream"

    def test_unknown_scheme_appends_path(self) -> None:
        url = _ws_url_from_base("wss://already-ws.example.com")
        assert url == "wss://already-ws.example.com/v1/twitter/stream"

    def test_trailing_slash_not_added_twice(self) -> None:
        # base_url should not have trailing slash per convention
        url = _ws_url_from_base("https://api.test.scrapebadger.com")
        assert url.endswith("/v1/twitter/stream")
        assert "/v1/twitter/stream/v1" not in url


# ===========================================================================
# TestParseEvent
# ===========================================================================


class TestParseEvent:
    """Tests for the _parse_event dispatch function."""

    def test_parses_connected_event(self) -> None:
        raw = {
            "type": "connected",
            "connection_id": "abc-123",
            "api_key_id": "ak_test",
        }
        event = _parse_event(raw)
        assert isinstance(event, ConnectedEvent)
        assert event.connection_id == "abc-123"

    def test_parses_ping_event(self) -> None:
        raw = {"type": "ping", "timestamp": "2026-03-03T10:00:00+00:00"}
        event = _parse_event(raw)
        assert isinstance(event, PingEvent)
        assert event.timestamp == "2026-03-03T10:00:00+00:00"

    def test_parses_tweet_event(self) -> None:
        event = _parse_event(TWEET_EVENT_RAW)
        assert isinstance(event, TweetEvent)
        assert event.tweet_id == "1895234567890123456"

    def test_parses_error_event(self) -> None:
        raw = {"type": "error", "code": 4003, "message": "Connection limit exceeded"}
        event = _parse_event(raw)
        assert isinstance(event, ErrorEvent)
        assert event.code == 4003

    def test_unknown_event_type_returns_error_event(self) -> None:
        raw = {"type": "unknown_future_type", "data": "something"}
        event = _parse_event(raw)
        assert isinstance(event, ErrorEvent)
        assert event.code == 0
        assert "Unknown event type" in event.message

    def test_missing_type_field_returns_error_event(self) -> None:
        raw = {"data": "no type here"}
        event = _parse_event(raw)
        assert isinstance(event, ErrorEvent)
        assert event.code == 0


# ===========================================================================
# TestWebSocketStreamError
# ===========================================================================


class TestWebSocketStreamError:
    """Tests for the WebSocketStreamError exception."""

    def test_default_message(self) -> None:
        err = WebSocketStreamError()
        assert "WebSocket stream error" in str(err)
        assert err.code is None

    def test_with_code(self) -> None:
        err = WebSocketStreamError("Auth failed", code=4001)
        assert err.code == 4001
        assert err.message == "Auth failed"

    def test_inherits_from_scrapebadger_error(self) -> None:
        from scrapebadger._internal.exceptions import ScrapeBadgerError

        err = WebSocketStreamError("test", code=4003)
        assert isinstance(err, ScrapeBadgerError)

    def test_code_none_by_default(self) -> None:
        err = WebSocketStreamError("network failure")
        assert err.code is None

    def test_status_code_is_none_by_default(self) -> None:
        err = WebSocketStreamError("test error")
        assert err.status_code is None


# ===========================================================================
# TestStreamClient -- Monitor CRUD
# ===========================================================================


class TestStreamClient:
    """Tests for StreamClient monitor CRUD methods."""

    async def test_create_monitor_minimal(
        self, stream_client: StreamClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.post.return_value = MONITOR_RESPONSE
        monitor = await stream_client.create_monitor(
            name="Test Monitor",
            usernames=["elonmusk"],
            poll_interval_seconds=5.0,
        )
        assert isinstance(monitor, StreamMonitor)
        assert monitor.id == MONITOR_RESPONSE["id"]
        assert monitor.name == "Test Monitor"
        mock_base_client.post.assert_called_once()
        call_args = mock_base_client.post.call_args
        assert call_args[0][0] == "/v1/twitter/stream/monitors"
        body = call_args[1]["json"]
        assert body["name"] == "Test Monitor"
        assert body["usernames"] == ["elonmusk"]
        assert body["poll_interval_seconds"] == 5.0
        assert "webhook_url" not in body
        assert "webhook_secret" not in body

    async def test_create_monitor_with_webhook(
        self, stream_client: StreamClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.post.return_value = MONITOR_RESPONSE
        await stream_client.create_monitor(
            name="Test Monitor",
            usernames=["elonmusk"],
            poll_interval_seconds=10.0,
            webhook_url="https://example.com/hook",
            webhook_secret="s3cr3t",
        )
        body = mock_base_client.post.call_args[1]["json"]
        assert body["webhook_url"] == "https://example.com/hook"
        assert body["webhook_secret"] == "s3cr3t"

    async def test_list_monitors_default_params(
        self, stream_client: StreamClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = MONITOR_LIST_RESPONSE
        result = await stream_client.list_monitors()
        assert isinstance(result, StreamMonitorList)
        assert result.total == 1
        call_params = mock_base_client.get.call_args[1]["params"]
        assert call_params["page"] == 1
        assert call_params["page_size"] == 20
        assert "status" not in call_params

    async def test_list_monitors_with_status_filter(
        self, stream_client: StreamClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = MONITOR_LIST_RESPONSE
        await stream_client.list_monitors(status="active", page=2, page_size=10)
        call_params = mock_base_client.get.call_args[1]["params"]
        assert call_params["status"] == "active"
        assert call_params["page"] == 2
        assert call_params["page_size"] == 10

    async def test_get_monitor(
        self, stream_client: StreamClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = MONITOR_RESPONSE
        monitor = await stream_client.get_monitor("550e8400-e29b-41d4-a716-446655440001")
        assert isinstance(monitor, StreamMonitor)
        assert monitor.id == "550e8400-e29b-41d4-a716-446655440001"
        mock_base_client.get.assert_called_once_with(
            "/v1/twitter/stream/monitors/550e8400-e29b-41d4-a716-446655440001"
        )

    async def test_update_monitor_partial(
        self, stream_client: StreamClient, mock_base_client: MagicMock
    ) -> None:
        updated = {**MONITOR_RESPONSE, "name": "Renamed Monitor"}
        mock_base_client._request.return_value = updated
        monitor = await stream_client.update_monitor(
            "550e8400-e29b-41d4-a716-446655440001",
            name="Renamed Monitor",
        )
        assert monitor.name == "Renamed Monitor"
        call_args = mock_base_client._request.call_args
        assert call_args[0][0] == "PATCH"
        body = call_args[1]["json"]
        assert body == {"name": "Renamed Monitor"}

    async def test_update_monitor_sends_only_provided_fields(
        self, stream_client: StreamClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client._request.return_value = MONITOR_RESPONSE
        await stream_client.update_monitor(
            "550e8400-e29b-41d4-a716-446655440001",
            poll_interval_seconds=60.0,
        )
        body = mock_base_client._request.call_args[1]["json"]
        assert "poll_interval_seconds" in body
        assert "name" not in body
        assert "usernames" not in body

    async def test_update_monitor_status_field(
        self, stream_client: StreamClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client._request.return_value = {**MONITOR_RESPONSE, "status": "paused"}
        monitor = await stream_client.update_monitor(
            "550e8400-e29b-41d4-a716-446655440001",
            status="paused",
        )
        body = mock_base_client._request.call_args[1]["json"]
        assert body["status"] == "paused"
        assert monitor.status == MonitorStatus.PAUSED

    async def test_pause_monitor_calls_update_with_paused(
        self, stream_client: StreamClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client._request.return_value = {**MONITOR_RESPONSE, "status": "paused"}
        monitor = await stream_client.pause_monitor("550e8400-e29b-41d4-a716-446655440001")
        assert monitor.status == MonitorStatus.PAUSED
        body = mock_base_client._request.call_args[1]["json"]
        assert body["status"] == "paused"

    async def test_resume_monitor_calls_update_with_active(
        self, stream_client: StreamClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client._request.return_value = MONITOR_RESPONSE
        monitor = await stream_client.resume_monitor("550e8400-e29b-41d4-a716-446655440001")
        assert monitor.status == MonitorStatus.ACTIVE
        body = mock_base_client._request.call_args[1]["json"]
        assert body["status"] == "active"

    async def test_delete_monitor_calls_delete(
        self, stream_client: StreamClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client._request.return_value = {}
        result = await stream_client.delete_monitor("550e8400-e29b-41d4-a716-446655440001")
        assert result is None  # delete_monitor returns None
        call_args = mock_base_client._request.call_args
        assert call_args[0][0] == "DELETE"
        assert "550e8400-e29b-41d4-a716-446655440001" in call_args[0][1]


# ===========================================================================
# TestStreamClientLogs
# ===========================================================================


class TestStreamClientLogs:
    """Tests for StreamClient log retrieval methods."""

    async def test_list_delivery_logs_default_params(
        self, stream_client: StreamClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = {
            "logs": [DELIVERY_LOG_RESPONSE],
            "total": 1,
            "page": 1,
            "page_size": 20,
        }
        result = await stream_client.list_delivery_logs()
        assert isinstance(result, DeliveryLogList)
        assert result.total == 1
        params = mock_base_client.get.call_args[1]["params"]
        assert params["page"] == 1
        assert params["page_size"] == 20
        assert params["sort"] == "desc"

    async def test_list_delivery_logs_with_filters(
        self, stream_client: StreamClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = {
            "logs": [],
            "total": 0,
            "page": 1,
            "page_size": 20,
        }
        await stream_client.list_delivery_logs(
            monitor_id="monitor-uuid",
            author_username="elonmusk",
            delivery_status="webhook_delivered",
            sort="asc",
        )
        params = mock_base_client.get.call_args[1]["params"]
        assert params["monitor_id"] == "monitor-uuid"
        assert params["author_username"] == "elonmusk"
        assert params["delivery_status"] == "webhook_delivered"
        assert params["sort"] == "asc"

    async def test_list_delivery_logs_no_optional_filters_when_none(
        self, stream_client: StreamClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = {
            "logs": [],
            "total": 0,
            "page": 1,
            "page_size": 20,
        }
        await stream_client.list_delivery_logs()
        params = mock_base_client.get.call_args[1]["params"]
        assert "monitor_id" not in params
        assert "author_username" not in params
        assert "delivery_status" not in params

    async def test_list_billing_logs_default_params(
        self, stream_client: StreamClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = {
            "logs": [BILLING_LOG_RESPONSE],
            "total": 1,
            "page": 1,
            "page_size": 20,
        }
        result = await stream_client.list_billing_logs()
        assert isinstance(result, BillingLogList)
        assert result.total == 1
        params = mock_base_client.get.call_args[1]["params"]
        assert params["page"] == 1
        assert params["page_size"] == 20

    async def test_list_billing_logs_with_monitor_id(
        self, stream_client: StreamClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = {
            "logs": [],
            "total": 0,
            "page": 1,
            "page_size": 20,
        }
        await stream_client.list_billing_logs(monitor_id="monitor-uuid")
        params = mock_base_client.get.call_args[1]["params"]
        assert params["monitor_id"] == "monitor-uuid"

    async def test_list_billing_logs_no_monitor_id_when_none(
        self, stream_client: StreamClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = {
            "logs": [],
            "total": 0,
            "page": 1,
            "page_size": 20,
        }
        await stream_client.list_billing_logs()
        params = mock_base_client.get.call_args[1]["params"]
        assert "monitor_id" not in params


# ===========================================================================
# TestConnectContextManager
# ===========================================================================


class _FakeWebSocket:
    """A fake WebSocket that yields a fixed list of raw JSON strings.

    This avoids the complexity of correctly mocking dunder methods on MagicMock.
    The async `for msg in ws:` loop calls `ws.__aiter__()` then `ws.__anext__()`.
    """

    def __init__(self, messages: list[str]) -> None:
        self._messages = iter(messages)
        self.send = AsyncMock()

    def __aiter__(self) -> _FakeWebSocket:
        return self

    async def __anext__(self) -> str:
        try:
            return next(self._messages)
        except StopIteration as exc:
            raise StopAsyncIteration from exc


class _FakeWebSocketCtx:
    """Async context manager that yields a _FakeWebSocket."""

    def __init__(self, ws: _FakeWebSocket) -> None:
        self._ws = ws

    async def __aenter__(self) -> _FakeWebSocket:
        return self._ws

    async def __aexit__(self, *args: object) -> bool:
        return False


class TestConnectContextManager:
    """Tests for the connect() WebSocket async context manager.

    WebSocket mocking strategy:
    - We mock `websockets.connect` to return a _FakeWebSocketCtx.
    - _FakeWebSocket yields fixed raw JSON strings on async iteration.
    - This avoids the complexity of mocking dunder methods on MagicMock.
    """

    @staticmethod
    def _make_ws_ctx(raw_messages: list[str]) -> tuple[_FakeWebSocket, _FakeWebSocketCtx]:
        """Create a (fake_ws, fake_ws_ctx) pair for the given raw messages."""
        ws = _FakeWebSocket(raw_messages)
        ctx = _FakeWebSocketCtx(ws)
        return ws, ctx

    async def test_connect_yields_tweet_events(self, stream_client: StreamClient) -> None:
        connected_msg = {
            "type": "connected",
            "connection_id": "abc-123",
            "api_key_id": "ak_test",
        }
        raw_messages = [json.dumps(connected_msg), json.dumps(TWEET_EVENT_RAW)]
        _mock_ws, mock_ws_ctx = self._make_ws_ctx(raw_messages)

        with patch("websockets.connect", return_value=mock_ws_ctx):
            async with stream_client.connect() as events:
                collected = []
                async for event in events:
                    collected.append(event)

        assert len(collected) == 2
        assert isinstance(collected[0], ConnectedEvent)
        assert isinstance(collected[1], TweetEvent)

    async def test_connect_auto_responds_to_ping(self, stream_client: StreamClient) -> None:
        ping_msg = {"type": "ping", "timestamp": "2026-03-03T10:00:00+00:00"}
        raw_messages = [json.dumps(ping_msg)]
        mock_ws, mock_ws_ctx = self._make_ws_ctx(raw_messages)

        with patch("websockets.connect", return_value=mock_ws_ctx):
            async with stream_client.connect() as events:
                collected = []
                async for event in events:
                    collected.append(event)

        # Ping was yielded to caller AND pong was sent transparently
        assert len(collected) == 1
        assert isinstance(collected[0], PingEvent)
        mock_ws.send.assert_called_once_with(json.dumps({"type": "pong"}))

    async def test_connect_raises_on_auth_error(self, stream_client: StreamClient) -> None:
        error_msg = {"type": "error", "code": 4001, "message": "Invalid API key"}
        _mock_ws, mock_ws_ctx = self._make_ws_ctx([json.dumps(error_msg)])

        with (
            patch("websockets.connect", return_value=mock_ws_ctx),
            pytest.raises(WebSocketStreamError) as exc_info,
        ):
            async with stream_client.connect() as events:
                async for _event in events:
                    pass

        assert exc_info.value.code == 4001

    async def test_connect_raises_on_connection_limit_error(
        self, stream_client: StreamClient
    ) -> None:
        error_msg = {"type": "error", "code": 4003, "message": "Connection limit exceeded"}
        _mock_ws, mock_ws_ctx = self._make_ws_ctx([json.dumps(error_msg)])

        with (
            patch("websockets.connect", return_value=mock_ws_ctx),
            pytest.raises(WebSocketStreamError) as exc_info,
        ):
            async with stream_client.connect() as events:
                async for _event in events:
                    pass

        assert exc_info.value.code == 4003

    async def test_connect_raises_on_unexpected_close_when_no_reconnect(
        self, stream_client: StreamClient
    ) -> None:
        from websockets.exceptions import ConnectionClosed

        class _ClosingWs:
            """WebSocket that raises ConnectionClosed on first __anext__."""

            send = AsyncMock()

            def __aiter__(self) -> _ClosingWs:
                return self

            async def __anext__(self) -> str:
                raise ConnectionClosed(None, None)  # type: ignore[arg-type]

        ws = _ClosingWs()
        ctx = _FakeWebSocketCtx(ws)  # type: ignore[arg-type]

        with (
            patch("websockets.connect", return_value=ctx),
            pytest.raises(WebSocketStreamError),
        ):
            async with stream_client.connect(reconnect=False) as events:
                async for _event in events:
                    pass

    async def test_connect_reconnects_after_connection_close(
        self, stream_client: StreamClient
    ) -> None:
        """On ConnectionClosed with reconnect=True the client should reconnect."""
        from websockets.exceptions import ConnectionClosed

        connect_call_count = 0

        class _FirstWs:
            """Raises ConnectionClosed on first message."""

            send = AsyncMock()

            def __aiter__(self) -> _FirstWs:
                return self

            async def __anext__(self) -> str:
                raise ConnectionClosed(None, None)  # type: ignore[arg-type]

        class _SecondWs:
            """Yields one tweet then stops."""

            send = AsyncMock()
            _yielded = False

            def __aiter__(self) -> _SecondWs:
                return self

            async def __anext__(self) -> str:
                if not self._yielded:
                    self._yielded = True
                    return json.dumps(TWEET_EVENT_RAW)
                raise StopAsyncIteration

        def _make_ctx(*_args: object, **_kwargs: object) -> _FakeWebSocketCtx:
            nonlocal connect_call_count
            connect_call_count += 1
            ws: _FakeWebSocket | _FirstWs | _SecondWs = (
                _FirstWs() if connect_call_count == 1 else _SecondWs()
            )
            return _FakeWebSocketCtx(ws)  # type: ignore[arg-type]

        with (
            patch("websockets.connect", side_effect=_make_ctx),
            patch("asyncio.sleep", new=AsyncMock()),
        ):
            async with stream_client.connect(
                reconnect=True,
                reconnect_delay_seconds=5.0,
                max_reconnects=2,
            ) as events:
                collected = []
                async for event in events:
                    collected.append(event)
                    # Stop once we get the tweet from the second connection
                    if isinstance(event, TweetEvent):
                        break

        # After reconnect, TweetEvent should have been received
        assert any(isinstance(e, TweetEvent) for e in collected)
        assert connect_call_count == 2

    async def test_connect_respects_max_reconnects(self, stream_client: StreamClient) -> None:
        from websockets.exceptions import ConnectionClosed

        class _AlwaysFailWs:
            send = AsyncMock()

            def __aiter__(self) -> _AlwaysFailWs:
                return self

            async def __anext__(self) -> str:
                raise ConnectionClosed(None, None)  # type: ignore[arg-type]

        def _make_ctx(*_args: object, **_kwargs: object) -> _FakeWebSocketCtx:
            return _FakeWebSocketCtx(_AlwaysFailWs())  # type: ignore[arg-type]

        with (
            patch("websockets.connect", side_effect=_make_ctx),
            patch("asyncio.sleep", new=AsyncMock()),
            pytest.raises(WebSocketStreamError) as exc_info,
        ):
            async with stream_client.connect(
                reconnect=True,
                reconnect_delay_seconds=5.0,
                max_reconnects=0,
            ) as events:
                async for _event in events:
                    pass

        assert "Max reconnects" in str(exc_info.value)

    async def test_connect_ignores_invalid_json(self, stream_client: StreamClient) -> None:
        # Mix invalid JSON with a valid tweet
        raw_messages = ["not-valid-json!!!", json.dumps(TWEET_EVENT_RAW)]
        _mock_ws, mock_ws_ctx = self._make_ws_ctx(raw_messages)

        with patch("websockets.connect", return_value=mock_ws_ctx):
            async with stream_client.connect() as events:
                collected = []
                async for event in events:
                    collected.append(event)

        # Invalid JSON was skipped; tweet was delivered
        assert len(collected) == 1
        assert isinstance(collected[0], TweetEvent)

    async def test_connect_uses_api_key_header(self, stream_client: StreamClient) -> None:
        _mock_ws, mock_ws_ctx = self._make_ws_ctx([])

        with patch("websockets.connect", return_value=mock_ws_ctx) as mock_connect:
            async with stream_client.connect() as events:
                async for _ in events:
                    pass

        call_kwargs = mock_connect.call_args[1]
        assert "additional_headers" in call_kwargs
        assert call_kwargs["additional_headers"]["x-api-key"] == "test_api_key_12345"

    async def test_connect_uses_correct_ws_url(self, stream_client: StreamClient) -> None:
        _mock_ws, mock_ws_ctx = self._make_ws_ctx([])

        with patch("websockets.connect", return_value=mock_ws_ctx) as mock_connect:
            async with stream_client.connect() as events:
                async for _ in events:
                    pass

        # base_url is "https://api.test.scrapebadger.com"
        called_url = mock_connect.call_args[0][0]
        assert called_url == "wss://api.test.scrapebadger.com/v1/twitter/stream"

    async def test_connect_enforces_min_reconnect_delay(self, stream_client: StreamClient) -> None:
        """reconnect_delay_seconds below the floor of 5s should be clamped to 5s."""
        from websockets.exceptions import ConnectionClosed

        sleep_calls: list[float] = []

        async def _mock_sleep(delay: float) -> None:
            sleep_calls.append(delay)

        class _AlwaysFailWs2:
            send = AsyncMock()

            def __aiter__(self) -> _AlwaysFailWs2:
                return self

            async def __anext__(self) -> str:
                raise ConnectionClosed(None, None)  # type: ignore[arg-type]

        def _make_ctx(*_args: object, **_kwargs: object) -> _FakeWebSocketCtx:
            return _FakeWebSocketCtx(_AlwaysFailWs2())  # type: ignore[arg-type]

        with (
            patch("websockets.connect", side_effect=_make_ctx),
            patch("asyncio.sleep", side_effect=_mock_sleep),
            pytest.raises(WebSocketStreamError),
        ):
            async with stream_client.connect(
                reconnect=True,
                reconnect_delay_seconds=0.001,  # below floor
                max_reconnects=0,  # fail after first reconnect attempt
            ) as events:
                async for _event in events:
                    pass

        # Even though 0.001 was passed, minimum 5s should be enforced
        if sleep_calls:
            assert sleep_calls[0] >= 5.0


# ===========================================================================
# TestTwitterClientStreamProperty
# ===========================================================================


class TestTwitterClientStreamProperty:
    """Tests that TwitterClient exposes the stream sub-client correctly."""

    def test_stream_property_returns_stream_client(self) -> None:
        from scrapebadger.twitter.client import TwitterClient

        mock_client = MagicMock()
        mock_client.config.api_key = "key"
        mock_client.config.base_url = "https://scrapebadger.com"

        twitter = TwitterClient(mock_client)
        assert isinstance(twitter.stream, StreamClient)

    def test_stream_property_same_instance(self) -> None:
        from scrapebadger.twitter.client import TwitterClient

        mock_client = MagicMock()
        twitter = TwitterClient(mock_client)
        assert twitter.stream is twitter.stream


# ===========================================================================
# TestVerifyWebhookSignature
# ===========================================================================


class TestVerifyWebhookSignature:
    """Tests for the verify_webhook_signature helper."""

    def _make_signature(self, secret: str, body: bytes) -> str:
        import hashlib
        import hmac as _hmac

        digest = _hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
        return f"sha256={digest}"

    def test_valid_signature_with_bytes(self) -> None:
        body = b'{"type":"tweet","tweet_id":"123"}'
        sig = self._make_signature("my-secret", body)
        assert verify_webhook_signature("my-secret", body, sig) is True

    def test_valid_signature_with_str(self) -> None:
        body_str = '{"type":"tweet","tweet_id":"123"}'
        sig = self._make_signature("my-secret", body_str.encode())
        assert verify_webhook_signature("my-secret", body_str, sig) is True

    def test_invalid_signature_returns_false(self) -> None:
        body = b'{"type":"tweet"}'
        sig = self._make_signature("wrong-secret", body)
        assert verify_webhook_signature("my-secret", body, sig) is False

    def test_missing_prefix_returns_false(self) -> None:
        assert verify_webhook_signature("s", b"body", "not-sha256=abc") is False

    def test_empty_signature_returns_false(self) -> None:
        assert verify_webhook_signature("s", b"body", "") is False

    def test_tampered_body_returns_false(self) -> None:
        body = b'{"original":true}'
        sig = self._make_signature("my-secret", body)
        assert verify_webhook_signature("my-secret", b'{"tampered":true}', sig) is False

    def test_importable_from_twitter_init(self) -> None:
        from scrapebadger.twitter import verify_webhook_signature as fn

        assert callable(fn)
