"""Tests for async requests (submit/get/wait/callback_status), the account webhook
methods and the scrapebadger.webhooks helpers (SCR-652)."""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, patch

import httpx
import pytest
import respx

import scrapebadger
from scrapebadger import (
    AsyncRequest,
    AsyncRequestTimeoutError,
    CallbackStatus,
    NotFoundError,
    PermissionDeniedError,
    ScrapeBadger,
    ScrapeBadgerError,
    ServerError,
    WebhookDeliveries,
    WebhookEvent,
    WebhookSecret,
    webhooks,
)

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

BASE = "https://api.test.scrapebadger.com"
ASK = f"{BASE}/v1/perplexity/ask"


@pytest.fixture
async def sb() -> AsyncGenerator[ScrapeBadger, None]:
    async with ScrapeBadger(api_key="test_key", base_url=BASE, max_retries=0) as client:
        yield client


@pytest.fixture
async def sb_retry() -> AsyncGenerator[ScrapeBadger, None]:
    async with ScrapeBadger(api_key="test_key", base_url=BASE, max_retries=2) as client:
        yield client


@pytest.fixture
def no_sleep():
    # Poll waits and the shared retry backoff both await asyncio.sleep.
    with patch("scrapebadger.agent.client.asyncio.sleep", new_callable=AsyncMock) as sleep:
        yield sleep


def accepted(request_id: str = "req-1", retry_after: int = 5, **headers: str) -> httpx.Response:
    return httpx.Response(
        202,
        headers={
            "Location": f"/v1/requests/{request_id}",
            "Retry-After": str(retry_after),
            **headers,
        },
        json={
            "request_id": request_id,
            "status": "running",
            "retry_after_seconds": retry_after,
            "next_action": {"method": "GET", "url": f"/v1/requests/{request_id}"},
        },
    )


ANSWER = {"answer": "HubSpot, Pipedrive", "sources": ["https://example.com"]}


def completed(status: int = 200, body: object = ANSWER, **headers: str) -> httpx.Response:
    return httpx.Response(
        status,
        headers={"X-Request-ID": "req-1", "X-Credits-Used": "20", **headers},
        json=body,
    )


# =============================================================================
# submit
# =============================================================================


class TestSubmit:
    @respx.mock
    async def test_202_is_running_and_sends_async_headers(self, sb: ScrapeBadger) -> None:
        route = respx.get(ASK).mock(return_value=accepted())
        req = await sb.requests.submit(
            "/v1/perplexity/ask",
            params={"prompt": "best crm", "country": None},
            callback_url="https://example.com/hook",
            idempotency_key="crm-1",
        )

        assert isinstance(req, AsyncRequest)
        assert req.status == "running"
        assert req.running is True
        assert req.request_id == "req-1"
        assert req.status_code == 202
        assert req.retry_after_seconds == 5
        assert req.body is None
        assert req.replayed is False

        sent = route.calls.last.request
        assert sent.headers["Prefer"] == "respond-async, wait=0"  # callback: answer at once
        assert sent.headers["X-Callback-URL"] == "https://example.com/hook"
        assert sent.headers["Idempotency-Key"] == "crm-1"
        assert dict(sent.url.params) == {"prompt": "best crm"}

    @respx.mock
    async def test_200_inline_is_completed(self, sb: ScrapeBadger) -> None:
        route = respx.get(ASK).mock(return_value=completed())
        req = await sb.requests.submit("perplexity/ask", params={"prompt": "x"}, wait=30)

        assert req.status == "completed"
        assert req.running is False
        assert req.request_id == "req-1"
        assert req.status_code == 200
        assert req.body == ANSWER
        assert req.data == ANSWER
        assert req.headers["x-credits-used"] == "20"
        assert req.credits_used == 20
        assert req.retry_after_seconds is None

        sent = route.calls.last.request
        assert sent.headers["Prefer"] == "respond-async, wait=30"
        assert "X-Callback-URL" not in sent.headers
        assert "Idempotency-Key" not in sent.headers

    @respx.mock
    async def test_without_wait_or_callback_uses_api_default(self, sb: ScrapeBadger) -> None:
        route = respx.get(ASK).mock(return_value=accepted())
        await sb.requests.submit("/v1/perplexity/ask", params={"prompt": "x"})
        assert route.calls.last.request.headers["Prefer"] == "respond-async"

    @respx.mock
    async def test_post_with_json_body(self, sb: ScrapeBadger) -> None:
        route = respx.post(f"{BASE}/v1/chatgpt/ask").mock(return_value=accepted("req-2"))
        req = await sb.requests.submit(
            "/v1/chatgpt/ask", method="post", json={"prompt": "x"}, wait=0
        )

        assert req.request_id == "req-2"
        assert json.loads(route.calls.last.request.content) == {"prompt": "x"}

    @respx.mock
    async def test_idempotent_replay_sets_replayed(self, sb: ScrapeBadger) -> None:
        respx.get(ASK).mock(return_value=completed(**{"Idempotent-Replayed": "true"}))
        req = await sb.requests.submit("/v1/perplexity/ask", idempotency_key="crm-1")

        assert req.replayed is True
        assert req.status == "completed"
        assert req.body == ANSWER

    @respx.mock
    async def test_idempotent_replay_of_running_call(self, sb: ScrapeBadger) -> None:
        respx.get(ASK).mock(return_value=accepted(**{"Idempotent-Replayed": "true"}))
        req = await sb.requests.submit("/v1/perplexity/ask", idempotency_key="crm-1")

        assert req.replayed is True
        assert req.status == "running"

    @respx.mock
    async def test_key_reused_for_another_call_raises_409(self, sb: ScrapeBadger) -> None:
        respx.get(ASK).mock(
            return_value=httpx.Response(
                409, json={"error": "idempotency_key_reused", "detail": "different call"}
            )
        )
        with pytest.raises(ScrapeBadgerError) as exc:
            await sb.requests.submit("/v1/perplexity/ask", idempotency_key="crm-1")
        assert exc.value.status_code == 409
        assert exc.value.response_data["error"] == "idempotency_key_reused"

    @respx.mock
    async def test_invalid_callback_url_raises_400(self, sb: ScrapeBadger) -> None:
        respx.get(ASK).mock(
            return_value=httpx.Response(
                400, json={"error": "invalid_callback_url", "detail": "must be https"}
            )
        )
        with pytest.raises(ScrapeBadgerError) as exc:
            await sb.requests.submit("/v1/perplexity/ask", callback_url="http://x")
        assert exc.value.status_code == 400

    @pytest.mark.parametrize("wait", [-1, 121, 2.5, True])
    async def test_rejects_bad_wait(self, sb: ScrapeBadger, wait: object) -> None:
        with pytest.raises(ValueError, match="wait"):
            await sb.requests.submit("/v1/perplexity/ask", wait=wait)  # type: ignore[arg-type]

    @pytest.mark.parametrize("key", ["", "has space", "é", "x" * 201])
    async def test_rejects_bad_idempotency_key(self, sb: ScrapeBadger, key: str) -> None:
        with pytest.raises(ValueError, match="idempotency_key"):
            await sb.requests.submit("/v1/perplexity/ask", idempotency_key=key)

    @pytest.mark.parametrize("path", ["", "https://scrapebadger.com/v1/perplexity/ask"])
    async def test_rejects_bad_path(self, sb: ScrapeBadger, path: str) -> None:
        with pytest.raises(ValueError, match="path"):
            await sb.requests.submit(path)

    @respx.mock
    async def test_lost_answer_is_not_resent_without_key(
        self, sb_retry: ScrapeBadger, no_sleep: AsyncMock
    ) -> None:
        route = respx.get(ASK).mock(side_effect=httpx.ReadTimeout("lost"))
        with pytest.raises(httpx.ReadTimeout):
            await sb_retry.requests.submit("/v1/perplexity/ask")
        assert route.call_count == 1  # a resend could start (and bill) a second call

    @respx.mock
    async def test_unsent_request_is_retried_without_key(
        self, sb_retry: ScrapeBadger, no_sleep: AsyncMock
    ) -> None:
        route = respx.get(ASK).mock(side_effect=[httpx.ConnectError("refused"), accepted()])
        req = await sb_retry.requests.submit("/v1/perplexity/ask")
        assert req.status == "running"
        assert route.call_count == 2

    @respx.mock
    async def test_lost_answer_is_resent_with_key(
        self, sb_retry: ScrapeBadger, no_sleep: AsyncMock
    ) -> None:
        route = respx.get(ASK).mock(
            side_effect=[
                httpx.ReadTimeout("lost"),
                accepted(**{"Idempotent-Replayed": "true"}),
            ]
        )
        req = await sb_retry.requests.submit("/v1/perplexity/ask", idempotency_key="k-1")
        assert route.call_count == 2
        assert req.replayed is True

    @respx.mock
    async def test_replayed_error_is_not_retried(
        self, sb_retry: ScrapeBadger, no_sleep: AsyncMock
    ) -> None:
        route = respx.get(ASK).mock(
            return_value=httpx.Response(
                502, headers={"Idempotent-Replayed": "true"}, json={"detail": "no answer"}
            )
        )
        with pytest.raises(ServerError):
            await sb_retry.requests.submit("/v1/perplexity/ask", idempotency_key="k-1")
        assert route.call_count == 1  # a stored result can't change


# =============================================================================
# get / wait / callback_status
# =============================================================================


POLL = f"{BASE}/v1/requests/req-1"


class TestGet:
    @respx.mock
    async def test_completed_has_status_code_headers_and_body(self, sb: ScrapeBadger) -> None:
        respx.get(POLL).mock(
            return_value=completed(201, {"created": True}, **{"X-Callback-Status": "delivered"})
        )
        state = await sb.requests.get("req-1")

        assert state.status == "completed"
        assert state.status_code == 201
        assert state.body == {"created": True}
        assert state.headers["x-callback-status"] == "delivered"
        assert state.credits_used == 20
        assert state.replayed is False

    @respx.mock
    async def test_running(self, sb: ScrapeBadger) -> None:
        respx.get(POLL).mock(return_value=accepted(retry_after=3))
        state = await sb.requests.get("req-1")

        assert state.status == "running"
        assert state.retry_after_seconds == 3
        assert state.headers == {}
        assert state.data["next_action"]["url"] == "/v1/requests/req-1"

    @respx.mock
    async def test_text_body_is_returned_as_text(self, sb: ScrapeBadger) -> None:
        respx.get(POLL).mock(
            return_value=httpx.Response(
                200, headers={"Content-Type": "text/html; charset=utf-8"}, text="<html>ok</html>"
            )
        )
        state = await sb.requests.get("req-1")
        assert state.body == "<html>ok</html>"

    @respx.mock
    async def test_request_id_is_path_quoted(self, sb: ScrapeBadger) -> None:
        route = respx.get(f"{BASE}/v1/requests/a%2Fb").mock(return_value=completed())
        await sb.requests.get("a/b")
        assert route.called


class TestWait:
    @respx.mock
    async def test_polls_until_done_honouring_retry_after(
        self, sb: ScrapeBadger, no_sleep: AsyncMock
    ) -> None:
        route = respx.get(POLL).mock(
            side_effect=[accepted(retry_after=5), accepted(retry_after=2), completed()]
        )
        done = await sb.requests.wait("req-1", timeout=60)

        assert done.status == "completed"
        assert done.body == ANSWER
        assert route.call_count == 3
        assert [c.args[0] for c in no_sleep.await_args_list] == [5, 2]

    @respx.mock
    async def test_uses_retry_after_header_without_body_hint(
        self, sb: ScrapeBadger, no_sleep: AsyncMock
    ) -> None:
        respx.get(POLL).mock(
            side_effect=[
                httpx.Response(202, headers={"Retry-After": "7"}, json={"status": "running"}),
                completed(),
            ]
        )
        await sb.requests.wait("req-1")
        assert no_sleep.await_args_list[0].args[0] == 7

    @respx.mock
    async def test_timeout_raises_and_keeps_request_id(
        self, sb: ScrapeBadger, no_sleep: AsyncMock
    ) -> None:
        route = respx.get(POLL).mock(return_value=accepted(retry_after=5))
        with (
            patch("scrapebadger.agent.client.monotonic", side_effect=[0.0, 0.0, 5.0, 10.0]),
            pytest.raises(AsyncRequestTimeoutError) as exc,
        ):
            await sb.requests.wait("req-1", timeout=7)

        assert isinstance(exc.value, TimeoutError)
        assert exc.value.request_id == "req-1"
        assert exc.value.timeout == 7
        assert route.call_count == 3
        # The last sleep is cut to what is left of the timeout.
        assert [c.args[0] for c in no_sleep.await_args_list] == [5, 2]

    @respx.mock
    async def test_zero_timeout_polls_once(self, sb: ScrapeBadger, no_sleep: AsyncMock) -> None:
        route = respx.get(POLL).mock(return_value=accepted())
        with pytest.raises(AsyncRequestTimeoutError):
            await sb.requests.wait("req-1", timeout=0)
        assert route.call_count == 1
        no_sleep.assert_not_awaited()

    @respx.mock
    async def test_error_result_is_raised_without_retry(
        self, sb_retry: ScrapeBadger, no_sleep: AsyncMock
    ) -> None:
        route = respx.get(POLL).mock(
            return_value=httpx.Response(502, json={"detail": "no usable answer"})
        )
        with pytest.raises(ServerError):
            await sb_retry.requests.wait("req-1")
        assert route.call_count == 1
        no_sleep.assert_not_awaited()

    @respx.mock
    async def test_expired_request_raises_not_found(self, sb: ScrapeBadger) -> None:
        respx.get(POLL).mock(return_value=httpx.Response(404, json={"error": "request_not_found"}))
        with pytest.raises(NotFoundError):
            await sb.requests.wait("req-1")


class TestCallbackStatus:
    @respx.mock
    async def test_parses_delivery_state(self, sb: ScrapeBadger) -> None:
        respx.get(f"{POLL}/callback").mock(
            return_value=httpx.Response(
                200,
                json={
                    "request_id": "req-1",
                    "state": "pending",
                    "attempts": 2,
                    "last_status": 503,
                    "last_error": "HTTPStatusError",
                    "next_attempt_at": 1793139000,
                    "delivered_at": None,
                    "callback_host": "example.com",
                },
            )
        )
        cb = await sb.requests.callback_status("req-1")

        assert isinstance(cb, CallbackStatus)
        assert cb.state == "pending"
        assert cb.attempts == 2
        assert cb.last_status == 503
        assert cb.next_attempt_at == 1793139000
        assert cb.delivered_at is None
        assert cb.callback_host == "example.com"

    @respx.mock
    async def test_no_callback_raises_not_found(self, sb: ScrapeBadger) -> None:
        respx.get(f"{POLL}/callback").mock(
            return_value=httpx.Response(404, json={"error": "callback_not_found"})
        )
        with pytest.raises(NotFoundError):
            await sb.requests.callback_status("req-1")


def test_async_request_keeps_the_old_constructor() -> None:
    old = AsyncRequest(request_id="r", running=True, status_code=202)
    assert old.status == "running"
    new = AsyncRequest(request_id="r", status="completed", status_code=200)
    assert new.running is False


# =============================================================================
# account
# =============================================================================


SECRET = {
    "secret": "whsec_test",
    "signature_header": "X-ScrapeBadger-Signature",
    "algorithm": "sha256=<hex HMAC-SHA256 of the raw request body>",
}


class TestAccount:
    @respx.mock
    async def test_webhook_secret_and_rotate(self, sb: ScrapeBadger) -> None:
        respx.get(f"{BASE}/v1/account/webhook-secret").mock(
            return_value=httpx.Response(200, json=SECRET)
        )
        rotate = respx.post(f"{BASE}/v1/account/webhook-secret/rotate").mock(
            return_value=httpx.Response(200, json={**SECRET, "secret": "whsec_new"})
        )

        secret = await sb.account.webhook_secret()
        assert isinstance(secret, WebhookSecret)
        assert secret.secret == "whsec_test"
        assert (await sb.account.rotate_webhook_secret()).secret == "whsec_new"
        assert rotate.called

    @respx.mock
    async def test_webhook_deliveries(self, sb: ScrapeBadger) -> None:
        route = respx.get(f"{BASE}/v1/account/webhook-deliveries").mock(
            return_value=httpx.Response(
                200,
                json={
                    "deliveries": [
                        {
                            "request_id": "req-1",
                            "endpoint": "/v1/perplexity/ask",
                            "state": "delivered",
                            "attempts": 1,
                            "last_status": 200,
                            "last_error": None,
                            "created_at": 1793138851,
                            "delivered_at": 1793138852,
                            "callback_host": "example.com",
                        }
                    ],
                    "window_hours": 24,
                },
            )
        )
        result = await sb.account.webhook_deliveries(limit=10)

        assert route.calls.last.request.url.params["limit"] == "10"
        assert isinstance(result, WebhookDeliveries)
        assert result.window_hours == 24
        assert result.deliveries[0].state == "delivered"
        assert result.deliveries[0].endpoint == "/v1/perplexity/ask"

    @respx.mock
    async def test_restricted_key_raises_permission_denied(self, sb: ScrapeBadger) -> None:
        respx.get(f"{BASE}/v1/account/webhook-deliveries").mock(
            return_value=httpx.Response(
                403, json={"error": "full_access_required", "detail": "needs a full key"}
            )
        )
        with pytest.raises(PermissionDeniedError):
            await sb.account.webhook_deliveries()

    def test_generated_methods_are_kept(self, sb: ScrapeBadger) -> None:
        for name in (
            "get_account_info",
            "get_the_webhook_signing_secret",
            "rotate_the_webhook_signing_secret",
        ):
            assert callable(getattr(sb.account, name))


# =============================================================================
# webhooks
# =============================================================================


def sign(secret: str, body: bytes) -> str:
    return "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


EVENT = {
    "event": "request.completed",
    "request_id": "6ca4ab7a-1",
    "batch_id": None,
    "status": 200,
    "headers": {"content-type": "application/json", "x-credits-used": "20"},
    "body": {"answer": "…", "sources": ["…"]},
    "body_size": 4812,
    "result_url": "https://scrapebadger.com/v1/requests/6ca4ab7a-1",
    "result_expires_at": 1793139751,
    "attempt": 1,
    "sent_at": 1793138851,
}
RAW = json.dumps(EVENT).encode()


class TestVerifySignature:
    def test_valid(self) -> None:
        assert webhooks.verify_signature("whsec_test", RAW, sign("whsec_test", RAW))

    def test_str_body_and_padded_header(self) -> None:
        sig = sign("whsec_test", RAW)
        assert webhooks.verify_signature("whsec_test", RAW.decode(), f" {sig} ")

    @pytest.mark.parametrize(
        "signature",
        [
            sign("whsec_other", RAW),  # wrong secret
            sign("whsec_test", RAW + b" "),  # tampered body
            sign("whsec_test", RAW).removeprefix("sha256="),  # no scheme
            sign("whsec_test", RAW).upper(),
            "sha256=é",
            "",
            None,
        ],
    )
    def test_invalid(self, signature: str | None) -> None:
        assert not webhooks.verify_signature("whsec_test", RAW, signature)

    def test_empty_secret_never_verifies(self) -> None:
        assert not webhooks.verify_signature("", RAW, sign("", RAW))

    def test_fresh_sent_at(self) -> None:
        now = time.time()
        sig = sign("whsec_test", RAW)
        assert webhooks.verify_signature("whsec_test", RAW, sig, sent_at=int(now) - 10)
        assert webhooks.verify_signature("whsec_test", RAW, sig, sent_at=str(int(now)))

    def test_stale_or_future_sent_at(self) -> None:
        now = time.time()
        sig = sign("whsec_test", RAW)
        assert not webhooks.verify_signature("whsec_test", RAW, sig, sent_at=now - 301)
        assert not webhooks.verify_signature("whsec_test", RAW, sig, sent_at=now + 301)
        assert webhooks.verify_signature(
            "whsec_test", RAW, sig, sent_at=now - 3000, tolerance_s=3600
        )

    @pytest.mark.parametrize("sent_at", ["soon", "nan", "inf"])
    def test_unreadable_sent_at(self, sent_at: str) -> None:
        assert not webhooks.verify_signature(
            "whsec_test", RAW, sign("whsec_test", RAW), sent_at=sent_at
        )

    def test_uses_constant_time_compare(self) -> None:
        with patch("scrapebadger.webhooks.hmac.compare_digest", return_value=True) as cmp:
            assert webhooks.verify_signature("whsec_test", RAW, "sha256=00")
        cmp.assert_called_once()


class TestParseEvent:
    def test_parses_payload(self) -> None:
        event = webhooks.parse_event(RAW)

        assert isinstance(event, WebhookEvent)
        assert event.event == "request.completed"
        assert event.request_id == "6ca4ab7a-1"
        assert event.batch_id is None
        assert event.status == 200
        assert event.headers["x-credits-used"] == "20"
        assert event.body == {"answer": "…", "sources": ["…"]}
        assert event.body_omitted is False
        assert event.body_size == 4812
        assert event.result_url.endswith("/v1/requests/6ca4ab7a-1")
        assert event.result_expires_at == 1793139751
        assert event.attempt == 1
        assert event.sent_at == 1793138851

    def test_omitted_body(self) -> None:
        raw = json.dumps({**EVENT, "body": None, "body_omitted": True, "batch_id": "b-1"})
        event = webhooks.parse_event(raw)
        assert event.body is None
        assert event.body_omitted is True
        assert event.batch_id == "b-1"

    @pytest.mark.parametrize("raw", [b"not json", b"[]", b'{"event": "request.completed"}'])
    def test_invalid_raises_value_error(self, raw: bytes) -> None:
        with pytest.raises(ValueError):
            webhooks.parse_event(raw)

    def test_verify_with_parsed_sent_at(self) -> None:
        raw = json.dumps({**EVENT, "sent_at": int(time.time())}).encode()
        event = webhooks.parse_event(raw)
        assert webhooks.verify_signature(
            "whsec_test", raw, sign("whsec_test", raw), sent_at=event.sent_at
        )


def test_public_exports() -> None:
    assert scrapebadger.webhooks is webhooks
    assert scrapebadger.verify_signature is webhooks.verify_signature
    assert scrapebadger.parse_event is webhooks.parse_event
    for name in (
        "AsyncRequestTimeoutError",
        "CallbackStatus",
        "WebhookDeliveries",
        "WebhookDelivery",
        "WebhookEvent",
        "WebhookSecret",
        "verify_signature",
        "parse_event",
        "webhooks",
    ):
        assert name in scrapebadger.__all__
    assert scrapebadger.__version__ == "0.80.0"
