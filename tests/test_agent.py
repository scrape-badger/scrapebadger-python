"""Tests for the agent platform clients: quote, feedback, results and requests."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import httpx
import pytest
import respx

from scrapebadger import AgentTrial, AsyncRequest, FeedbackReceipt, Quote, ScrapeBadger
from scrapebadger._internal.exceptions import NotFoundError, ServerError
from scrapebadger.agent import AgentClient, RequestsClient, ResultsClient

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

BASE = "https://api.test.scrapebadger.com"


@pytest.fixture
async def sb() -> AsyncGenerator[ScrapeBadger, None]:
    async with ScrapeBadger(api_key="test_key", base_url=BASE, max_retries=0) as client:
        yield client


QUOTE = {
    "method": "GET",
    "path": "/v1/google/search",
    "scraper": "google",
    "endpoint_pattern": "search",
    "valid": False,
    "errors": [{"field": "q", "message": "required"}],
    "billing": "flat",
    "credits": {"min": 0, "max": 20, "base": 20, "per_item": 0},
    "usd": {"max_per_call_list": 0.004, "per_1k_calls_list": 4.0, "per_1k_calls_best": 2.0},
    "latency": {"p50_ms": 900, "p95_ms": 2500, "p99_ms": 6000, "samples": 1234, "window_days": 30},
    "notes": ["Empty or blocked results are not billed."],
}


def test_wired_onto_top_level_client() -> None:
    client = ScrapeBadger(api_key="test_key")
    assert isinstance(client.agent, AgentClient)
    assert isinstance(client.results, ResultsClient)
    assert isinstance(client.requests, RequestsClient)


class TestQuote:
    @respx.mock
    async def test_posts_call_and_parses_quote(self, sb: ScrapeBadger) -> None:
        route = respx.post(f"{BASE}/v1/quote").mock(return_value=httpx.Response(200, json=QUOTE))
        quote = await sb.agent.quote("GET", "/v1/google/search", params={"hl": "en"})

        assert json.loads(route.calls.last.request.content) == {
            "method": "GET",
            "path": "/v1/google/search",
            "params": {"hl": "en"},
        }
        assert isinstance(quote, Quote)
        assert quote.valid is False
        assert quote.errors[0].field == "q"
        assert quote.credits.max == 20
        assert quote.usd is not None
        assert quote.usd.per_1k_calls_best == 2.0
        assert quote.latency is not None
        assert quote.latency.p95_ms == 2500

    @respx.mock
    async def test_unbounded_per_item_and_no_latency(self, sb: ScrapeBadger) -> None:
        body = {
            **QUOTE,
            "valid": None,
            "errors": [],
            "billing": "per_item",
            "credits": {"min": 0, "max": None, "base": 1, "per_item": 0.5},
            "latency": None,
        }
        route = respx.post(f"{BASE}/v1/quote").mock(return_value=httpx.Response(200, json=body))
        quote = await sb.agent.quote("POST", "web/scrape", body={"url": "https://x.com"})

        assert json.loads(route.calls.last.request.content)["body"] == {"url": "https://x.com"}
        assert quote.valid is None
        assert quote.credits.max is None
        assert quote.credits.per_item == 0.5
        assert quote.latency is None

    @respx.mock
    async def test_unknown_endpoint_carries_suggestions(self, sb: ScrapeBadger) -> None:
        respx.post(f"{BASE}/v1/quote").mock(
            return_value=httpx.Response(
                404,
                json={
                    "error": "unknown_endpoint",
                    "detail": "No endpoint GET /v1/google/serch.",
                    "suggestions": ["/v1/google/search"],
                },
            )
        )
        with pytest.raises(NotFoundError) as exc:
            await sb.agent.quote("GET", "/v1/google/serch")
        assert exc.value.response_data["suggestions"] == ["/v1/google/search"]


RECEIPT = {"id": "fb-1", "status": "received", "message": "Thanks"}


class TestFeedback:
    @respx.mock
    async def test_feedback_sends_only_given_fields(self, sb: ScrapeBadger) -> None:
        route = respx.post(f"{BASE}/v1/feedback").mock(
            return_value=httpx.Response(201, json=RECEIPT)
        )
        receipt = await sb.agent.feedback("Need a Maps photos endpoint", details="for listings")

        assert json.loads(route.calls.last.request.content) == {
            "type": "feedback",
            "summary": "Need a Maps photos endpoint",
            "details": "for listings",
        }
        assert isinstance(receipt, FeedbackReceipt)
        assert receipt.id == "fb-1"

    @respx.mock
    async def test_report_bug_sets_type_bug(self, sb: ScrapeBadger) -> None:
        route = respx.post(f"{BASE}/v1/feedback").mock(
            return_value=httpx.Response(201, json=RECEIPT)
        )
        await sb.agent.report_bug(
            "Empty results",
            request_id="req-1",
            endpoint="/v1/google/search",
            contact="me@example.com",
        )

        assert json.loads(route.calls.last.request.content) == {
            "type": "bug",
            "summary": "Empty results",
            "request_id": "req-1",
            "endpoint": "/v1/google/search",
            "contact": "me@example.com",
        }


class TestResults:
    @respx.mock
    async def test_plain_view_params(self, sb: ScrapeBadger) -> None:
        route = respx.get(f"{BASE}/v1/results/res-1").mock(
            return_value=httpx.Response(200, json=["a", "b"])
        )
        data = await sb.results.get(
            "res-1", jq=".results[].title", fields=["title", "link"], max_items=5, summary=True
        )

        params = route.calls.last.request.url.params
        assert params["jq"] == ".results[].title"
        assert params["fields"] == "title,link"
        assert params["max_items"] == "5"
        assert params["summary"] == "true"
        assert not any(k.startswith("_") for k in params)
        assert data == ["a", "b"]

    @respx.mock
    async def test_no_view_params_by_default(self, sb: ScrapeBadger) -> None:
        route = respx.get(f"{BASE}/v1/results/res-1").mock(
            return_value=httpx.Response(200, json={"results": []})
        )
        assert await sb.results.get("res-1") == {"results": []}
        assert not route.calls.last.request.url.params

    @respx.mock
    async def test_expired_result_raises_not_found(self, sb: ScrapeBadger) -> None:
        respx.get(f"{BASE}/v1/results/gone").mock(
            return_value=httpx.Response(
                404, json={"error": "result_not_found", "detail": "expired"}
            )
        )
        with pytest.raises(NotFoundError):
            await sb.results.get("gone")


class TestRequests:
    @respx.mock
    async def test_running(self, sb: ScrapeBadger) -> None:
        respx.get(f"{BASE}/v1/requests/req-1").mock(
            return_value=httpx.Response(
                202,
                headers={"Retry-After": "5", "Location": "/v1/requests/req-1"},
                json={
                    "request_id": "req-1",
                    "status": "running",
                    "retry_after_seconds": 5,
                    "next_action": {"method": "GET", "url": "/v1/requests/req-1"},
                },
            )
        )
        state = await sb.requests.get("req-1")

        assert isinstance(state, AsyncRequest)
        assert state.running is True
        assert state.status_code == 202
        assert state.retry_after_seconds == 5
        assert state.result_id is None

    @respx.mock
    async def test_done_returns_original_body_and_headers(self, sb: ScrapeBadger) -> None:
        respx.get(f"{BASE}/v1/requests/req-1").mock(
            return_value=httpx.Response(
                200,
                headers={"X-Credits-Used": "20", "X-Result-ID": "req-1"},
                json={"status": "ok", "results": [1, 2]},
            )
        )
        state = await sb.requests.get("req-1")

        assert state.running is False
        assert state.status_code == 200
        assert state.retry_after_seconds is None
        assert state.result_id == "req-1"
        assert state.credits_used == 20
        assert state.data == {"status": "ok", "results": [1, 2]}

    @respx.mock
    async def test_original_error_status_raises(self, sb: ScrapeBadger) -> None:
        respx.get(f"{BASE}/v1/requests/req-1").mock(
            return_value=httpx.Response(502, json={"detail": "upstream failed"})
        )
        with pytest.raises(ServerError):
            await sb.requests.get("req-1")

    @respx.mock
    async def test_unknown_request_raises_not_found(self, sb: ScrapeBadger) -> None:
        respx.get(f"{BASE}/v1/requests/nope").mock(
            return_value=httpx.Response(
                404, json={"error": "request_not_found", "detail": "not billed"}
            )
        )
        with pytest.raises(NotFoundError):
            await sb.requests.get("nope")

    @respx.mock
    async def test_batch_submits_items_and_parses_each_outcome(self, sb: ScrapeBadger) -> None:
        route = respx.post(f"{BASE}/v1/batch").mock(
            return_value=httpx.Response(
                202,
                json={
                    "batch_id": "b-1",
                    "count": 2,
                    "accepted": 1,
                    "requests": [
                        {
                            "index": 0,
                            "accepted": True,
                            "status": 202,
                            "request_id": "r-0",
                            "poll_url": "/v1/requests/r-0",
                        },
                        {
                            "index": 1,
                            "accepted": False,
                            "status": 429,
                            "request_id": "r-1",
                            "error": {"detail": "Rate limit exceeded"},
                        },
                    ],
                },
            )
        )
        items = [{"path": "/v1/chatgpt/ask", "query": {"prompt": p}} for p in ("a", "b")]
        sub = await sb.requests.batch(items, callback_url="https://example.com/hook")

        assert json.loads(route.calls[0].request.content) == {
            "requests": items,
            "callback_url": "https://example.com/hook",
        }
        assert sub.batch_id == "b-1" and sub.accepted == 1
        assert sub.requests[0].poll_url == "/v1/requests/r-0"
        assert not sub.requests[1].accepted and sub.requests[1].status == 429


def test_agent_trial_block_parses() -> None:
    trial = AgentTrial.model_validate(
        {
            "credits_remaining": 42,
            "expires_at": "2026-10-30T00:00:00Z",
            "claim_url": "https://scrapebadger.com/claim-key?token=t",
        }
    )
    assert trial.credits_remaining == 42
    assert trial.claim_url is not None
