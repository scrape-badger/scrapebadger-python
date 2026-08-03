"""Tests for 5xx retry warning logging and default max_retries."""

from __future__ import annotations

import logging
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from scrapebadger._internal.client import BaseClient
from scrapebadger._internal.config import ClientConfig
from scrapebadger._internal.exceptions import ScrapeBadgerError


@pytest.fixture
def config_one_retry() -> ClientConfig:
    """Config with a single retry so tests run fast."""
    return ClientConfig(api_key="test_key", max_retries=1)


@pytest.fixture
def config_default() -> ClientConfig:
    """Config using the real default max_retries."""
    return ClientConfig(api_key="test_key")


class TestDefaultMaxRetries:
    """Tests for the default max_retries value."""

    def test_default_max_retries_is_ten(self, config_default: ClientConfig) -> None:
        """Default max_retries must be 10 per Feature 2 spec."""
        assert config_default.max_retries == 10

    def test_with_overrides_preserves_default(self, config_default: ClientConfig) -> None:
        """with_overrides keeps the new default when max_retries is not overridden."""
        new_cfg = config_default.with_overrides(timeout=60.0)
        assert new_cfg.max_retries == 10

    def test_with_overrides_can_change_retries(self, config_default: ClientConfig) -> None:
        """with_overrides can still change max_retries explicitly."""
        new_cfg = config_default.with_overrides(max_retries=3)
        assert new_cfg.max_retries == 3


class TestRetryWarningLogging:
    """Tests that warning logs are emitted on 5xx retries and network errors."""

    def _make_response(self, status_code: int, reason: str = "") -> httpx.Response:
        """Build a minimal httpx.Response stub."""
        mock_resp = MagicMock(spec=httpx.Response)
        mock_resp.status_code = status_code
        mock_resp.reason_phrase = reason or httpx.codes.get_reason_phrase(status_code)
        mock_resp.headers = httpx.Headers({})
        mock_resp.json.return_value = {}
        return mock_resp

    async def test_warning_logged_on_503_retry(
        self,
        config_one_retry: ClientConfig,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Emits a WARNING through 'scrapebadger' logger when retrying on 503."""
        fail_resp = self._make_response(503)
        ok_resp = self._make_response(200)
        ok_resp.json.return_value = {"ok": True}

        client = BaseClient(config_one_retry)
        mock_http = AsyncMock()
        mock_http.request.side_effect = [fail_resp, ok_resp]

        with (
            patch.object(client, "_get_client", return_value=mock_http),
            patch("scrapebadger._internal.client.asyncio.sleep"),
            caplog.at_level(logging.WARNING, logger="scrapebadger"),
        ):
            result = await client.get("/v1/test")

        assert result == {"ok": True}
        warning_records = [r for r in caplog.records if r.levelno == logging.WARNING]
        assert warning_records, "Expected at least one WARNING log on 503 retry"
        assert any(r.name == "scrapebadger" for r in warning_records)

    async def test_warning_message_format_5xx(
        self,
        config_one_retry: ClientConfig,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Warning message matches expected format for 5xx errors."""
        fail_resp = self._make_response(503, "Service Unavailable")
        ok_resp = self._make_response(200)
        ok_resp.json.return_value = {}

        client = BaseClient(config_one_retry)
        mock_http = AsyncMock()
        mock_http.request.side_effect = [fail_resp, ok_resp]

        with (
            patch.object(client, "_get_client", return_value=mock_http),
            patch("scrapebadger._internal.client.asyncio.sleep"),
            caplog.at_level(logging.WARNING, logger="scrapebadger"),
        ):
            await client.get("/v1/test")

        msgs = [r.message for r in caplog.records if r.levelno == logging.WARNING]
        assert msgs, "Expected warning messages"
        msg = msgs[0]
        assert "503" in msg
        assert "Service Unavailable" in msg
        assert "retrying" in msg.lower()
        assert "1/1" in msg  # attempt n/max

    async def test_warning_logged_on_network_error_retry(
        self,
        config_one_retry: ClientConfig,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Emits a WARNING when retrying after a network-level error."""
        ok_resp = MagicMock(spec=httpx.Response)
        ok_resp.status_code = 200
        ok_resp.reason_phrase = "OK"
        ok_resp.headers = httpx.Headers({})
        ok_resp.json.return_value = {"ok": True}

        client = BaseClient(config_one_retry)
        mock_http = AsyncMock()
        mock_http.request.side_effect = [
            httpx.ConnectError("Connection refused"),
            ok_resp,
        ]

        with (
            patch.object(client, "_get_client", return_value=mock_http),
            patch("scrapebadger._internal.client.asyncio.sleep"),
            caplog.at_level(logging.WARNING, logger="scrapebadger"),
        ):
            result = await client.get("/v1/test")

        assert result == {"ok": True}
        warning_records = [r for r in caplog.records if r.levelno == logging.WARNING]
        assert warning_records, "Expected WARNING log on network error retry"

    async def test_warning_message_format_network_error(
        self,
        config_one_retry: ClientConfig,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Warning message for network errors includes error type."""
        ok_resp = self._make_response(200)
        ok_resp.json.return_value = {}

        client = BaseClient(config_one_retry)
        mock_http = AsyncMock()
        mock_http.request.side_effect = [
            httpx.ConnectError("Connection refused"),
            ok_resp,
        ]

        with (
            patch.object(client, "_get_client", return_value=mock_http),
            patch("scrapebadger._internal.client.asyncio.sleep"),
            caplog.at_level(logging.WARNING, logger="scrapebadger"),
        ):
            await client.get("/v1/test")

        msgs = [r.message for r in caplog.records if r.levelno == logging.WARNING]
        assert msgs
        msg = msgs[0]
        assert "ConnectError" in msg
        assert "retrying" in msg.lower()

    async def test_no_warning_logged_on_404(
        self,
        config_one_retry: ClientConfig,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Does NOT log a warning for non-retryable 4xx errors."""
        fail_resp = self._make_response(404, "Not Found")
        fail_resp.json.return_value = {"detail": "Not found"}

        client = BaseClient(config_one_retry)
        mock_http = AsyncMock()
        mock_http.request.return_value = fail_resp

        with (
            patch.object(client, "_get_client", return_value=mock_http),
            caplog.at_level(logging.WARNING, logger="scrapebadger"),
            pytest.raises(ScrapeBadgerError),
        ):
            await client.get("/v1/test")

        warning_records = [r for r in caplog.records if r.levelno == logging.WARNING]
        assert not warning_records, "Should not log warnings for 404"

    async def test_500_is_retried(
        self,
        config_one_retry: ClientConfig,
    ) -> None:
        """A transient 500 is retried rather than raising immediately.

        Regression: 500 was missing from retry_on_status, so a single transient
        500 mid-pagination killed long-running scrapes outright.
        """
        fail_resp = self._make_response(500, "Internal Server Error")
        ok_resp = self._make_response(200)
        ok_resp.json.return_value = {"ok": True}

        client = BaseClient(config_one_retry)
        mock_http = AsyncMock()
        mock_http.request.side_effect = [fail_resp, ok_resp]

        with (
            patch.object(client, "_get_client", return_value=mock_http),
            patch("scrapebadger._internal.client.asyncio.sleep"),
        ):
            result = await client.get("/v1/test")

        assert result == {"ok": True}
        assert mock_http.request.call_count == 2

    async def test_502_then_500_recovers(self) -> None:
        """The real-world 502 → 500 → 200 sequence survives.

        This is the exact sequence that failed two Apify runs: the 502 retried,
        the retry came back 500, and 500 was not retryable.
        """
        client = BaseClient(ClientConfig(api_key="test_key", max_retries=5))
        ok_resp = self._make_response(200)
        ok_resp.json.return_value = {"ok": True}

        mock_http = AsyncMock()
        mock_http.request.side_effect = [
            self._make_response(502, "Bad Gateway"),
            self._make_response(500, "Internal Server Error"),
            ok_resp,
        ]

        with (
            patch.object(client, "_get_client", return_value=mock_http),
            patch("scrapebadger._internal.client.asyncio.sleep"),
        ):
            result = await client.get("/v1/test")

        assert result == {"ok": True}
        assert mock_http.request.call_count == 3

    @pytest.mark.parametrize(
        "exc",
        [
            httpx.ConnectTimeout("timed out"),
            httpx.PoolTimeout("pool exhausted"),
            httpx.ReadTimeout("read timed out"),
            httpx.ConnectError("connection refused"),
            httpx.RemoteProtocolError("server disconnected"),
            httpx.ProxyError("proxy failed"),
        ],
        ids=lambda e: type(e).__name__,
    )
    async def test_transport_errors_are_retried(
        self,
        config_one_retry: ClientConfig,
        exc: Exception,
    ) -> None:
        """Every transient transport failure is retried, not just the original three."""
        ok_resp = self._make_response(200)
        ok_resp.json.return_value = {"ok": True}

        client = BaseClient(config_one_retry)
        mock_http = AsyncMock()
        mock_http.request.side_effect = [exc, ok_resp]

        with (
            patch.object(client, "_get_client", return_value=mock_http),
            patch("scrapebadger._internal.client.asyncio.sleep"),
        ):
            result = await client.get("/v1/test")

        assert result == {"ok": True}
        assert mock_http.request.call_count == 2

    @pytest.mark.parametrize(
        "exc",
        [
            httpx.UnsupportedProtocol("unsupported scheme"),
            httpx.LocalProtocolError("malformed request"),
        ],
        ids=lambda e: type(e).__name__,
    )
    async def test_caller_errors_are_not_retried(
        self,
        config_one_retry: ClientConfig,
        exc: Exception,
    ) -> None:
        """Config/caller mistakes fail fast instead of burning the retry budget."""
        client = BaseClient(config_one_retry)
        mock_http = AsyncMock()
        mock_http.request.side_effect = exc

        with (
            patch.object(client, "_get_client", return_value=mock_http),
            pytest.raises(type(exc)),
        ):
            await client.get("/v1/test")

        assert mock_http.request.call_count == 1

    async def test_get_with_headers_returns_data_and_headers(
        self,
        config_one_retry: ClientConfig,
    ) -> None:
        """get_with_headers returns a (data, headers) tuple."""
        resp_headers = httpx.Headers(
            {
                "X-RateLimit-Limit": "300",
                "X-RateLimit-Remaining": "250",
                "X-RateLimit-Reset": "1700000060",
                "Content-Type": "application/json",
            }
        )
        ok_resp = MagicMock(spec=httpx.Response)
        ok_resp.status_code = 200
        ok_resp.reason_phrase = "OK"
        ok_resp.headers = resp_headers
        ok_resp.json.return_value = {"data": []}

        client = BaseClient(config_one_retry)
        mock_http = AsyncMock()
        mock_http.request.return_value = ok_resp

        with patch.object(client, "_get_client", return_value=mock_http):
            data, headers = await client.get_with_headers("/v1/test")

        assert data == {"data": []}
        # httpx.Headers normalises names to lowercase when converted to a plain dict
        assert headers["x-ratelimit-limit"] == "300"
        assert headers["x-ratelimit-remaining"] == "250"
        assert headers["x-ratelimit-reset"] == "1700000060"

    async def test_get_with_headers_warning_on_5xx_retry(
        self,
        config_one_retry: ClientConfig,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """get_with_headers also logs warnings on 5xx retries."""
        fail_resp = self._make_response(503, "Service Unavailable")
        ok_resp = MagicMock(spec=httpx.Response)
        ok_resp.status_code = 200
        ok_resp.reason_phrase = "OK"
        ok_resp.headers = httpx.Headers({})
        ok_resp.json.return_value = {}

        client = BaseClient(config_one_retry)
        mock_http = AsyncMock()
        mock_http.request.side_effect = [fail_resp, ok_resp]

        with (
            patch.object(client, "_get_client", return_value=mock_http),
            patch("scrapebadger._internal.client.asyncio.sleep"),
            caplog.at_level(logging.WARNING, logger="scrapebadger"),
        ):
            await client.get_with_headers("/v1/test")

        warning_records = [r for r in caplog.records if r.levelno == logging.WARNING]
        assert warning_records, "get_with_headers should emit warnings on retry"
