"""Agent platform API clients.

Free helpers around the scraper APIs: quote a call before making it, report a
bug, re-read a recent result, and poll a call made with
``Prefer: respond-async``. None of these calls is ever billed.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from scrapebadger.agent.models import AsyncRequest, BatchSubmission, FeedbackReceipt, Quote

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class AgentClient:
    """Client for quoting calls and sending feedback.

    Example:
        ```python
        async with ScrapeBadger(api_key="your-key") as client:
            quote = await client.agent.quote("GET", "/v1/google/search", params={"q": "x"})
            print(quote.valid, quote.credits.max, quote.usd.max_per_call_list)

            await client.agent.report_bug(
                "Empty organic results for a valid query",
                request_id="<X-Request-ID of the failing call>",
                endpoint="/v1/google/search",
            )
        ```

    Note:
        This client is not instantiated directly. Instead, access it through
        the `agent` property of the main `ScrapeBadger` client.
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize the agent client.

        Args:
            client: The base HTTP client for making API requests.
        """
        self._client = client

    async def quote(
        self,
        method: Literal["GET", "POST"],
        path: str,
        *,
        params: dict[str, Any] | None = None,
        body: dict[str, Any] | None = None,
    ) -> Quote:
        """Quote a call: its cost, whether its parameters are valid, and its latency.

        Free: nothing runs and nothing is charged.

        Args:
            method: HTTP method of the call to quote.
            path: Path of the call, e.g. "/v1/google/search" (the "/v1" prefix
                is optional).
            params: The call's query parameters.
            body: The call's JSON body (POST endpoints).

        Returns:
            Quote with credits, USD, validation errors and latency.

        Raises:
            NotFoundError: No such endpoint. ``e.response_data["suggestions"]``
                lists close matches.
        """
        payload: dict[str, Any] = {"method": method, "path": path}
        if params is not None:
            payload["params"] = params
        if body is not None:
            payload["body"] = body
        response = await self._client.post("/v1/quote", json=payload)
        return Quote.model_validate(response)

    async def feedback(
        self,
        summary: str,
        *,
        kind: Literal["bug", "feedback"] = "feedback",
        details: str | None = None,
        request_id: str | None = None,
        endpoint: str | None = None,
        contact: str | None = None,
    ) -> FeedbackReceipt:
        """Send feedback (an API or field you needed and couldn't find) or a bug report.

        Free, never billed; rate limited per key (429 when over the limit).

        Args:
            summary: One-line summary, 3-200 characters.
            kind: "feedback" or "bug" (sent as the ``type`` field).
            details: Longer description, up to 5,000 characters.
            request_id: ``X-Request-ID`` of the call concerned, so it can be found.
            endpoint: Path of the endpoint concerned, e.g. "/v1/google/search".
            contact: Where to reach you, if you want a reply.

        Returns:
            FeedbackReceipt with the report ID.
        """
        payload: dict[str, Any] = {"type": kind, "summary": summary}
        optional = {
            "details": details,
            "request_id": request_id,
            "endpoint": endpoint,
            "contact": contact,
        }
        payload.update({k: v for k, v in optional.items() if v is not None})
        response = await self._client.post("/v1/feedback", json=payload)
        return FeedbackReceipt.model_validate(response)

    async def report_bug(
        self,
        summary: str,
        *,
        details: str | None = None,
        request_id: str | None = None,
        endpoint: str | None = None,
        contact: str | None = None,
    ) -> FeedbackReceipt:
        """Report a bug: a wrong or empty result for valid input, a misleading
        error, or a price mismatch.

        Same as ``feedback(..., kind="bug")``.

        Args:
            summary: One-line summary, 3-200 characters.
            details: Longer description, up to 5,000 characters.
            request_id: ``X-Request-ID`` of the failing call, so it can be found.
            endpoint: Path of the endpoint concerned, e.g. "/v1/google/search".
            contact: Where to reach you, if you want a reply.

        Returns:
            FeedbackReceipt with the report ID.
        """
        return await self.feedback(
            summary,
            kind="bug",
            details=details,
            request_id=request_id,
            endpoint=endpoint,
            contact=contact,
        )


class ResultsClient:
    """Client for re-reading recent results for free.

    Every billed 2xx read carries an ``X-Result-ID`` header; the body is kept
    for about 15 minutes and can be replayed — optionally reshaped — without
    re-running (and re-paying for) the call.

    Note:
        This client is not instantiated directly. Instead, access it through
        the `results` property of the main `ScrapeBadger` client.
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize the results client.

        Args:
            client: The base HTTP client for making API requests.
        """
        self._client = client

    async def get(
        self,
        result_id: str,
        *,
        jq: str | None = None,
        fields: str | list[str] | None = None,
        max_items: int | None = None,
        summary: bool = False,
    ) -> Any:
        """Replay a recent result, optionally trimmed. Free.

        Args:
            result_id: ``X-Result-ID`` of the original call.
            jq: jq expression applied last, e.g. ".results[].title". A jq
                error returns ``{"_view_error", "result_id", "data"}``.
            fields: Fields to keep on each item of the main list, e.g.
                ["title", "link"] or "title,link" (dotted paths allowed).
            max_items: Keep at most this many items of the main list
                (adds a ``_truncated`` marker).
            summary: Return a structural outline (types, list lengths, byte
                sizes) instead of the body.

        Returns:
            The original response body, reshaped by the view params — any JSON
            value (object, list, string, number).

        Raises:
            NotFoundError: Unknown result, or it expired (~15 minutes).
        """
        params: dict[str, Any] = {
            "jq": jq,
            "fields": ",".join(fields) if isinstance(fields, list) else fields,
            "max_items": max_items,
        }
        if summary:
            params["summary"] = "true"
        return await self._client.get(f"/v1/results/{result_id}", params=params)


class RequestsClient:
    """Client for polling calls made with ``Prefer: respond-async``.

    A read sent with ``Prefer: respond-async, wait=25`` that doesn't finish
    within ``wait`` seconds answers 202 with a ``request_id``; poll it here
    until it is done. Never re-submit the original call.

    Note:
        This client is not instantiated directly. Instead, access it through
        the `requests` property of the main `ScrapeBadger` client.
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize the requests client.

        Args:
            client: The base HTTP client for making API requests.
        """
        self._client = client

    async def get(self, request_id: str) -> AsyncRequest:
        """Poll an async request. Free.

        Args:
            request_id: ``request_id`` from the 202 response.

        Returns:
            AsyncRequest. ``running`` is True while the call is in progress;
            once done, ``data`` holds the original response body.

        Raises:
            NotFoundError: Unknown or expired request. A request that never
                completed was not billed.
            ScrapeBadgerError: The original call finished with an error status
                (raised as the matching subclass).
        """
        data, headers, status_code = await self._client._request_with_status(
            "GET", f"/v1/requests/{request_id}"
        )
        lower = {k.lower(): v for k, v in headers.items()}
        running = status_code == 202
        retry_after = (
            data.get("retry_after_seconds") if running and isinstance(data, dict) else None
        )
        credits_used = lower.get("x-credits-used")
        return AsyncRequest(
            request_id=request_id,
            running=running,
            status_code=status_code,
            retry_after_seconds=retry_after,
            result_id=lower.get("x-result-id"),
            credits_used=int(credits_used) if credits_used and credits_used.isdigit() else None,
            data=data,
        )

    async def batch(
        self,
        requests: list[dict[str, Any]],
        *,
        callback_url: str | None = None,
    ) -> BatchSubmission:
        """Submit up to 100 GET reads as async requests in one call. Submitting is free.

        Each item runs under this key with the same auth, credit check, rate
        limit and price as if sent alone; at most 10 of a batch run at a time.

        Example:
            ```python
            sub = await client.requests.batch(
                [{"path": "/v1/chatgpt/ask", "query": {"prompt": p}} for p in prompts],
                callback_url="https://example.com/hook",
            )
            ids = [r.request_id for r in sub.requests if r.accepted]
            ```

        Args:
            requests: Items ``{"path": "/v1/...", "query": {...}}`` (``method``
                defaults to "GET").
            callback_url: https URL that gets one signed webhook per item when
                it completes. Verify it with ``verify_webhook_signature`` and the
                secret from ``GET /v1/account/webhook-secret``.

        Returns:
            BatchSubmission with a request_id (or the refusal) for every item.
        """
        payload: dict[str, Any] = {"requests": requests}
        if callback_url is not None:
            payload["callback_url"] = callback_url
        response = await self._client.post("/v1/batch", json=payload)
        return BatchSubmission.model_validate(response)
