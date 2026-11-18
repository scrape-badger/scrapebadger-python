"""Agent platform API clients.

Free helpers around the scraper APIs: quote a call before making it, report a
bug, and run any call asynchronously (submit, poll, wait, webhook status). None
of the helper calls is ever billed; an async call is billed once, like any
call, when it completes. (``results.get`` is deprecated: the API stopped storing
results on 2026-11-09.)
"""

from __future__ import annotations

import asyncio
import warnings
from time import monotonic
from typing import TYPE_CHECKING, Any, Literal
from urllib.parse import quote

from scrapebadger._internal.client import (
    RETRYABLE_TRANSPORT_ERRORS,
    UNSENT_TRANSPORT_ERRORS,
    _retry_after_seconds,
)
from scrapebadger._internal.exceptions import AsyncRequestTimeoutError, ScrapeBadgerError
from scrapebadger.agent.models import (
    AsyncRequest,
    BatchSubmission,
    CallbackStatus,
    FeedbackReceipt,
    Quote,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

    import httpx

    from scrapebadger._internal.client import BaseClient

# Prefer: respond-async, wait=N accepts 0..120 seconds.
MAX_ASYNC_WAIT_S = 120
# Poll interval when a 202 names none (the API sends 5).
_DEFAULT_POLL_S = 5
# Never poll faster than this, whatever Retry-After says.
_MIN_POLL_S = 1.0


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
    """Deprecated client for the removed ``GET /v1/results/{id}`` re-read.

    ScrapeBadger no longer stores results: responses carry no ``X-Result-ID``
    and ``GET /v1/results/{id}`` answers 410 Gone since 2026-11-09. To get a
    different shape of a result, re-run the call with the ``jq``, ``fields``
    or ``max_items`` view parameters (billed as a normal call).

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
        """Deprecated: the API no longer stores results, so there is nothing to re-read.

        ``GET /v1/results/{id}`` was removed from the API on 2026-11-09 and now
        answers 410 Gone, which this method raises as ``ScrapeBadgerError``.
        Re-run the original call with the ``jq``, ``fields`` or ``max_items``
        view parameters instead (billed as a normal call). Kept only so existing
        code fails with a clear error; it will be removed in a future release.

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
            ScrapeBadgerError: Always (410 Gone ``results_removed``) against the
                current API.
        """
        warnings.warn(
            "results.get() is deprecated: ScrapeBadger stopped storing results on "
            "2026-11-09 and GET /v1/results/{id} answers 410 Gone. Re-run the call "
            "with jq/fields/max_items view parameters instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        params: dict[str, Any] = {
            "jq": jq,
            "fields": ",".join(fields) if isinstance(fields, list) else fields,
            "max_items": max_items,
        }
        if summary:
            params["summary"] = "true"
        return await self._client.get(f"/v1/results/{result_id}", params=params)


def _api_path(path: str) -> str:
    """Normalise "perplexity/ask", "/perplexity/ask" or "/v1/perplexity/ask"."""
    p = path.strip()
    if not p or "://" in p:
        msg = f"Pass the API path, e.g. '/v1/perplexity/ask', not {path!r}"
        raise ValueError(msg)
    p = "/" + p.lstrip("/")
    return p if p.startswith("/v1/") else "/v1" + p


def _request_path(request_id: str) -> str:
    if not request_id:
        msg = "request_id is required"
        raise ValueError(msg)
    return "/v1/requests/" + quote(request_id, safe="")


def _decode_body(response: httpx.Response) -> Any:
    """Decoded JSON for a JSON response, else the text (as the webhook does).

    A body without a Content-Type is tried as JSON too, as earlier releases did.
    """
    content_type = response.headers.get("content-type", "").lower()
    if "json" in content_type or not content_type:
        try:
            return response.json()
        except ValueError:
            pass
    return response.text


def _to_async_request(response: httpx.Response, request_id: str | None = None) -> AsyncRequest:
    """Build an AsyncRequest from a submit or poll response (status below 400)."""
    replayed = response.headers.get("Idempotent-Replayed", "").strip().lower() == "true"
    data = _decode_body(response)
    fields = data if isinstance(data, dict) else {}
    if response.status_code == 202:
        retry_after = fields.get("retry_after_seconds")
        if not isinstance(retry_after, int) or isinstance(retry_after, bool):
            retry_after = (
                _retry_after_seconds(response, default=_DEFAULT_POLL_S)
                if "Retry-After" in response.headers
                else None
            )
        polled_id = str(fields.get("request_id") or response.headers.get("X-Request-ID", ""))
        return AsyncRequest(
            request_id=request_id or polled_id,
            status="running",
            running=True,
            status_code=202,
            retry_after_seconds=retry_after,
            replayed=replayed,
            data=data,
        )
    # Application-level error in a 2xx body: raised like on every other call.
    if fields.get("error"):
        raise ScrapeBadgerError(fields["error"], response.status_code, fields)
    credits_used = response.headers.get("X-Credits-Used", "")
    return AsyncRequest(
        request_id=request_id or response.headers.get("X-Request-ID", ""),
        status="completed",
        running=False,
        status_code=response.status_code,
        headers=dict(response.headers),
        body=data,
        replayed=replayed,
        credits_used=int(credits_used) if credits_used.isdigit() else None,
        data=data,
    )


class RequestsClient:
    """Run any call asynchronously: submit it, then poll, wait, or take its webhook.

    ``submit`` sends a call with ``Prefer: respond-async``. If it finishes within
    ``wait`` seconds you get the result at once (``status == "completed"``);
    otherwise a ``request_id`` to poll with ``get`` or ``wait`` (free), or to
    match against its webhook. Never re-submit a running call: that starts, and
    bills, a second one. Results are kept for about 15 minutes.

    Example:
        ```python
        async with ScrapeBadger(api_key="your-key") as client:
            req = await client.requests.submit(
                "/v1/perplexity/ask",
                params={"prompt": "best crm for startups"},
                idempotency_key="crm-question-2026-11-18",
            )
            done = await client.requests.wait(req.request_id, timeout=300)
            print(done.status_code, done.body)
        ```

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

    async def submit(
        self,
        path: str,
        *,
        method: str = "GET",
        params: Mapping[str, Any] | None = None,
        json: Any = None,
        callback_url: str | None = None,
        wait: int | None = None,
        idempotency_key: str | None = None,
    ) -> AsyncRequest:
        """Submit any API call asynchronously. Submitting is free; the call is billed
        once, when it completes.

        Example:
            ```python
            req = await client.requests.submit(
                "/v1/perplexity/ask",
                params={"prompt": "best crm for startups"},
                callback_url="https://example.com/hooks/scrapebadger",
                idempotency_key=f"crm-{row_id}",
            )
            # req.status == "running": the result arrives at the callback URL.
            ```

        Args:
            path: The call's path, e.g. "/v1/perplexity/ask" (the "/v1" prefix is
                optional).
            method: HTTP method of the call ("GET", "POST", ...).
            params: The call's query parameters (None values are dropped).
            json: The call's JSON body (POST endpoints).
            callback_url: https URL that gets a signed ``request.completed``
                webhook when the call completes (``X-Callback-URL``). Verify it
                with ``scrapebadger.webhooks.verify_signature``.
            wait: Seconds (0-120) to wait for the result before answering 202
                (``Prefer: respond-async, wait=N``). Default: 0 with a
                ``callback_url`` (answer at once), otherwise the API's default (25).
            idempotency_key: 1-200 visible ASCII characters (``Idempotency-Key``).
                Re-submitting the same call with the same key within 15 minutes
                does not run or bill it again: you get the first call's state
                (``replayed=True``). The same key with a different call raises
                ``ScrapeBadgerError`` 409 ``idempotency_key_reused``. With a key,
                the SDK also retries a submit whose answer was lost in transit.

        Returns:
            AsyncRequest: ``status="running"`` with ``request_id`` and
            ``retry_after_seconds``, or ``status="completed"`` with
            ``status_code``, ``headers`` and ``body`` when the call finished
            within ``wait``.

        Raises:
            ValueError: ``wait`` outside 0-120, an invalid ``idempotency_key`` or
                ``path``.
            ScrapeBadgerError: The call was refused (400 ``invalid_callback_url``,
                ``async_not_supported``, 409 ``idempotency_key_reused``, 402, 429...)
                or finished within ``wait`` with an error status (raised as the
                matching subclass). A refused call is not billed.
        """
        if wait is None and callback_url is not None:
            wait = 0
        if wait is not None and (
            isinstance(wait, bool) or not isinstance(wait, int) or not 0 <= wait <= MAX_ASYNC_WAIT_S
        ):
            msg = f"wait must be an int from 0 to {MAX_ASYNC_WAIT_S} seconds, got {wait!r}"
            raise ValueError(msg)
        headers = {"Prefer": "respond-async" if wait is None else f"respond-async, wait={wait}"}
        if callback_url is not None:
            headers["X-Callback-URL"] = callback_url
        if idempotency_key is not None:
            if not 1 <= len(idempotency_key) <= 200 or not all(
                "!" <= c <= "~" for c in idempotency_key
            ):
                msg = "idempotency_key must be 1-200 visible ASCII characters (no spaces)"
                raise ValueError(msg)
            headers["Idempotency-Key"] = idempotency_key
        response = await self._client._send(
            method.upper(),
            _api_path(path),
            params=params,
            json=json,
            headers=headers,
            # Without a key, a retry after the request got through would start and
            # bill a second call: only retry errors raised before it was sent.
            retry_transport=(
                RETRYABLE_TRANSPORT_ERRORS if idempotency_key else UNSENT_TRANSPORT_ERRORS
            ),
        )
        return _to_async_request(response)

    async def get(self, request_id: str) -> AsyncRequest:
        """Poll an async request. Free.

        Args:
            request_id: ``request_id`` from ``submit`` or the 202 response.

        Returns:
            AsyncRequest. ``status == "running"`` (``running`` is True) while the
            call is in progress; once done, ``status == "completed"`` with the
            original ``status_code``, ``headers`` and ``body``.

        Raises:
            NotFoundError: Unknown or expired request. A request that never
                completed was not billed.
            ScrapeBadgerError: The original call finished with an error status
                (raised as the matching subclass).
        """
        response = await self._client._send("GET", _request_path(request_id))
        return _to_async_request(response, request_id)

    async def wait(self, request_id: str, *, timeout: float = 600.0) -> AsyncRequest:
        """Poll until the request completes, sleeping ``Retry-After`` between polls. Free.

        Args:
            request_id: ``request_id`` from ``submit``.
            timeout: Give up after this many seconds (default 600). Results are
                kept for about 15 minutes after the call completes.

        Returns:
            The completed AsyncRequest (``status_code``, ``headers``, ``body``).

        Raises:
            AsyncRequestTimeoutError: Still running after ``timeout``. The call
                keeps running: poll it again or wait for its webhook; never
                re-submit it. Also a ``TimeoutError``.
            NotFoundError: Unknown or expired request.
            ScrapeBadgerError: The original call finished with an error status
                (raised as the matching subclass). A stored result can't change,
                so error statuses are raised at once, not retried.
        """
        if timeout < 0:
            msg = "timeout must be >= 0"
            raise ValueError(msg)
        path = _request_path(request_id)
        deadline = monotonic() + timeout
        while True:
            response = await self._client._send("GET", path, retry_status=False)
            state = _to_async_request(response, request_id)
            if state.status == "completed":
                return state
            remaining = deadline - monotonic()
            if remaining <= 0:
                msg = (
                    f"Request {request_id} is still running after {timeout:g} s. Poll it "
                    "again (free) or wait for its webhook; do not re-submit it."
                )
                raise AsyncRequestTimeoutError(
                    msg,
                    202,
                    state.data if isinstance(state.data, dict) else None,
                    request_id=request_id,
                    timeout=timeout,
                )
            delay = state.retry_after_seconds
            if delay is None:
                delay = _DEFAULT_POLL_S
            await asyncio.sleep(min(max(float(delay), _MIN_POLL_S), remaining))

    async def callback_status(self, request_id: str) -> CallbackStatus:
        """Read the delivery state of a request's webhook. Free.

        Args:
            request_id: A request submitted with a ``callback_url``.

        Returns:
            CallbackStatus with ``state``, ``attempts``, ``last_status``,
            ``last_error``, ``next_attempt_at`` and ``delivered_at``.

        Raises:
            NotFoundError: The request has no callback (404
                ``callback_not_found``), or its delivery record (kept 24 h) expired.
        """
        response = await self._client.get(f"{_request_path(request_id)}/callback")
        return CallbackStatus.model_validate(response)

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
                it completes. Verify it with ``scrapebadger.webhooks.verify_signature``
                and the secret from ``client.account.webhook_secret()``.

        Returns:
            BatchSubmission with a request_id (or the refusal) for every item.
        """
        payload: dict[str, Any] = {"requests": requests}
        if callback_url is not None:
            payload["callback_url"] = callback_url
        response = await self._client.post("/v1/batch", json=payload)
        return BatchSubmission.model_validate(response)
