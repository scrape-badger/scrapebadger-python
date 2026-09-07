"""Tests for 5xx retry warning logging and default max_retries."""

from __future__ import annotations

import asyncio
import logging
from email.utils import formatdate
from unittest.mock import AsyncMock, MagicMock, call, patch

import httpx
import pytest
import respx

from scrapebadger import ScrapeBadger
from scrapebadger._internal.client import BaseClient
from scrapebadger._internal.config import ClientConfig
from scrapebadger._internal.exceptions import RateLimitError, ScrapeBadgerError, ServerError


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


class TestRetryAfter:
    """Retry server capacity errors without ignoring the server's waiting period."""

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("5", 5),
            ("0", 1),
            (" 5 ", 5),
            (formatdate(1_800_000_005, usegmt=True), 5),
            ("Fri Jan 15 08:00:05 2027", 5),
            (formatdate(1_799_999_999, usegmt=True), 1),
            (None, 1),
            ("", 1),
            ("invalid", 1),
            ("-5", 1),
            ("1.5", 1),
            ("NaN", 1),
            ("Infinity", 1),
            pytest.param("9" * 400, 1, id="overflow"),
        ],
    )
    async def test_ai_mode_retry_after(
        self, respx_mock: respx.MockRouter, value: str | None, expected: int
    ) -> None:
        route = respx_mock.get("https://sdk.test/v1/google/ai-mode/search").mock(
            side_effect=[
                httpx.Response(503, headers={"Retry-After": value} if value is not None else {}),
                httpx.Response(200, json={"markdown": "A complete AI Mode answer"}),
            ]
        )
        with (
            patch("scrapebadger._internal.client.asyncio.sleep") as sleep,
            patch("scrapebadger._internal.client.time.time", return_value=1_800_000_000.25),
        ):
            async with ScrapeBadger(
                api_key="test_key", base_url="https://sdk.test", max_retries=1
            ) as client:
                answer = await client.google.ai_mode.search("Why is the sky blue?")

        assert answer == {"markdown": "A complete AI Mode answer"}
        assert route.call_count == 2
        sleep.assert_awaited_once_with(expected)

    @pytest.mark.parametrize("value", ["5", formatdate(1_800_000_005, usegmt=True), "invalid"])
    def test_ai_mode_from_synchronous_program(
        self, respx_mock: respx.MockRouter, value: str
    ) -> None:
        """The SDK is async-only; synchronous programs enter through asyncio.run()."""
        route = respx_mock.get("https://sdk.test/v1/google/ai-mode/search").mock(
            side_effect=[
                httpx.Response(503, headers={"Retry-After": value}),
                httpx.Response(200, json={"markdown": "Answer"}),
            ]
        )

        async def search() -> str:
            async with ScrapeBadger(
                api_key="test_key", base_url="https://sdk.test", max_retries=1
            ) as client:
                answer = await client.google.ai_mode.search("Why is the sky blue?")
                return str(answer["markdown"])

        with (
            patch("scrapebadger._internal.client.asyncio.sleep") as sleep,
            patch("scrapebadger._internal.client.time.time", return_value=1_800_000_000),
        ):
            assert asyncio.run(search()) == "Answer"

        sleep.assert_awaited_once_with(1 if value == "invalid" else 5)
        assert route.call_count == 2

    @pytest.mark.parametrize("status", [500, 502, 503, 504])
    @pytest.mark.parametrize("method", ["get", "get_with_headers", "post"])
    async def test_shared_retry_path(
        self, config_one_retry: ClientConfig, method: str, status: int
    ) -> None:
        async with BaseClient(config_one_retry) as client:
            with (
                patch.object(
                    client,
                    "_execute_request",
                    side_effect=[
                        httpx.Response(status, headers={"Retry-After": "5"}),
                        httpx.Response(200, json={"ok": True}),
                    ],
                ) as request,
                patch("scrapebadger._internal.client.asyncio.sleep") as sleep,
            ):
                result = await getattr(client, method)("/v1/test")
        assert (result[0] if method == "get_with_headers" else result) == {"ok": True}
        assert request.await_count == 2
        sleep.assert_awaited_once_with(5)

    async def test_retry_limit_and_backoff_are_preserved(self) -> None:
        async with BaseClient(ClientConfig(api_key="test_key", max_retries=5)) as client:
            with (
                patch.object(
                    client,
                    "_execute_request",
                    side_effect=[
                        httpx.Response(503, headers={"Retry-After": "5"}),
                        httpx.Response(503, headers={"Retry-After": "invalid"}),
                        httpx.ConnectTimeout("timeout"),
                        httpx.Response(503, headers={"Retry-After": "5"}),
                        httpx.ConnectTimeout("timeout"),
                        httpx.Response(503, headers={"Retry-After": "5"}),
                    ],
                ) as request,
                patch("scrapebadger._internal.client.asyncio.sleep") as sleep,
                pytest.raises(ServerError) as error,
            ):
                await client.get("/v1/test")
        assert error.value.status_code == 503
        assert request.await_count == 6
        assert sleep.await_args_list == [call(5), call(2), call(4), call(8), call(16)]

    @pytest.mark.parametrize(
        ("value", "expected"),
        [("5", 5), ("0", 0), (formatdate(1_800_000_005, usegmt=True), 5), ("invalid", 60)],
    )
    async def test_429_keeps_rate_limit_error_without_automatic_retry(
        self, config_one_retry: ClientConfig, value: str, expected: int
    ) -> None:
        async with BaseClient(config_one_retry) as client:
            with (
                patch.object(
                    client,
                    "_execute_request",
                    return_value=httpx.Response(429, headers={"Retry-After": value}),
                ) as request,
                patch("scrapebadger._internal.client.asyncio.sleep") as sleep,
                patch("scrapebadger._internal.client.time.time", return_value=1_800_000_000),
                pytest.raises(RateLimitError) as error,
            ):
                await client.get("/v1/test")
        assert error.value.retry_after == expected
        assert request.await_count == 1
        sleep.assert_not_awaited()


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
