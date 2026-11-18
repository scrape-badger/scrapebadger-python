"""Pydantic models for the agent platform endpoints.

Quote, feedback and async requests — the account-level helpers an agent uses
around the scraper APIs. None of these calls is ever billed (an async call is
billed once, like any call, when it completes). All models are immutable
(frozen) and ignore unknown fields for forward compatibility.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class _BaseModel(BaseModel):
    """Base model with common configuration."""

    model_config = ConfigDict(
        frozen=True,
        populate_by_name=True,
        extra="ignore",
    )


# =============================================================================
# Quote
# =============================================================================


class QuoteFieldError(_BaseModel):
    """One problem with the quoted call's parameters.

    Attributes:
        field: The parameter at fault.
        message: What is wrong with it, e.g. "required".
    """

    field: str | None = None
    message: str = ""


class QuoteCredits(_BaseModel):
    """What the call costs in credits.

    Attributes:
        min: Lowest possible charge (0 when an empty result is not billed).
        max: Highest possible charge. None when the call is billed per item
            and has no upper bound.
        base: Charge for one call before any per-item part.
        per_item: Charge per returned item (0 for flat-priced endpoints).
    """

    min: int = 0
    max: int | None = None
    base: int = 0
    per_item: float = 0


class QuoteUsd(_BaseModel):
    """What the call costs in USD.

    Attributes:
        max_per_call_list: Highest charge for one call at the Starter plan rate.
        per_1k_calls_list: 1,000 calls at the Starter plan rate.
        per_1k_calls_best: 1,000 calls at the cheapest plan rate.
        per_1k_items_list: 1,000 items at the Starter plan rate (per-item
            endpoints only).
    """

    max_per_call_list: float | None = None
    per_1k_calls_list: float | None = None
    per_1k_calls_best: float | None = None
    per_1k_items_list: float | None = None


class QuoteLatency(_BaseModel):
    """How long successful calls to this endpoint took recently.

    Attributes:
        p50_ms: Median latency in milliseconds.
        p95_ms: 95th percentile latency in milliseconds.
        p99_ms: 99th percentile latency in milliseconds.
        samples: Number of calls measured.
        window_days: Measurement window in days.
    """

    p50_ms: int | None = None
    p95_ms: int | None = None
    p99_ms: int | None = None
    samples: int = 0
    window_days: int | None = None


class Quote(_BaseModel):
    """What a call would cost, whether its parameters are valid, and how long it
    usually takes.

    Attributes:
        method: HTTP method of the quoted call.
        path: Normalised path of the quoted call (always starts with ``/v1/``).
        scraper: Scraper the path belongs to, e.g. "google".
        endpoint_pattern: Endpoint the path matched, e.g. "search".
        valid: True when the parameters validate, False when ``errors`` lists
            problems, None when this endpoint's parameters are not validated.
        errors: Parameter problems (empty when ``valid`` is not False).
        billing: "flat", "per_item", "dynamic" (web scraping) or "free".
        credits: Credit cost.
        usd: USD cost, or None when plan rates are unavailable.
        latency: Recent latency, or None until samples exist.
        notes: Billing caveats worth relaying, e.g. that empty results are free.
    """

    method: str = "GET"
    path: str = ""
    scraper: str | None = None
    endpoint_pattern: str | None = None
    valid: bool | None = None
    errors: list[QuoteFieldError] = Field(default_factory=list)
    billing: str | None = None
    credits: QuoteCredits = Field(default_factory=QuoteCredits)
    usd: QuoteUsd | None = None
    latency: QuoteLatency | None = None
    notes: list[str] = Field(default_factory=list)


# =============================================================================
# Feedback
# =============================================================================


class FeedbackReceipt(_BaseModel):
    """Acknowledgement of a bug report or feedback.

    Attributes:
        id: Report ID.
        status: Always "received".
        message: Text to relay; no reply is needed.
    """

    id: str = ""
    status: str = "received"
    message: str = ""


# =============================================================================
# Async requests
# =============================================================================


class AsyncRequest(_BaseModel):
    """State of an async call: submitted with ``requests.submit`` (or
    ``Prefer: respond-async``) and read back with ``requests.get`` / ``wait``.

    Attributes:
        request_id: The request's id (``X-Request-ID``).
        status: "running" while the call is in progress (HTTP 202), then
            "completed". Never re-submit a running call: poll it, or wait for
            its webhook.
        running: ``status == "running"`` (kept from earlier releases).
        status_code: 202 while running, then the original call's HTTP status.
        retry_after_seconds: Suggested wait before the next poll (running only).
        headers: The original call's response headers, lower-cased names
            (completed only), e.g. ``x-credits-used``.
        body: The original call's response body (completed only): decoded JSON
            for a JSON response, else the text.
        replayed: True when the API answered from an earlier call with the same
            ``Idempotency-Key`` (``Idempotent-Replayed: true``) instead of
            running it again. Nothing was billed for the replay.
        credits_used: ``X-Credits-Used`` of the finished call.
        result_id: Deprecated, always None. The API stopped sending
            ``X-Result-ID`` (and storing results for re-reads) on 2026-11-09.
        data: The response body as earlier releases returned it: ``body`` once
            completed, the 202 status body while running.
    """

    request_id: str
    status: Literal["running", "completed"]
    running: bool
    status_code: int
    retry_after_seconds: int | None = None
    headers: dict[str, str] = Field(default_factory=dict)
    body: Any = None
    replayed: bool = False
    credits_used: int | None = None
    result_id: str | None = None
    data: Any = None

    @model_validator(mode="before")
    @classmethod
    def _status_and_running(cls, values: Any) -> Any:
        """Accept either ``status`` or ``running`` and derive the other."""
        if isinstance(values, dict):
            if "status" not in values and "running" in values:
                values = {**values, "status": "running" if values["running"] else "completed"}
            elif "running" not in values and "status" in values:
                values = {**values, "running": values["status"] == "running"}
        return values


class CallbackStatus(_BaseModel):
    """Delivery state of a request's webhook (``requests.callback_status``).

    Only requests submitted with a ``callback_url`` have one. The delivery
    metadata is kept for 24 hours; it holds the callback host only, never its
    path or query.

    Attributes:
        request_id: The request the webhook is for.
        state: "pending" (not sent yet, or waiting for a retry), "delivering",
            "delivered" or "failed" (all attempts used, or a final status).
        attempts: Attempts made so far (at most 4: retries after 10 s, 60 s
            and 5 min).
        last_status: HTTP status your endpoint answered on the last attempt,
            or None (no answer, e.g. a timeout).
        last_error: Short error class of the last attempt, or None.
        next_attempt_at: Unix time of the next retry, or None.
        delivered_at: Unix time of the successful delivery, or None.
        callback_host: Host of the callback URL.
    """

    request_id: str
    state: str = "pending"
    attempts: int = 0
    last_status: int | None = None
    last_error: str | None = None
    next_attempt_at: int | float | None = None
    delivered_at: int | float | None = None
    callback_host: str | None = None


class BatchItemResult(_BaseModel):
    """One item of a ``requests.batch`` submission.

    Attributes:
        index: Position of the item in the submitted list.
        accepted: True when the item started; poll ``request_id`` (or wait for
            its webhook). False when it was refused before running (rate
            limit, credits, unknown endpoint...): not billed, resubmit later.
        status: HTTP status of the submission (202 when accepted).
        request_id: The item's request id (also set when refused, for bug reports).
        poll_url: Where to poll it (accepted items).
        error: The refusal's error body (refused items).
    """

    index: int
    accepted: bool
    status: int
    request_id: str | None = None
    poll_url: str | None = None
    error: Any = None


class BatchSubmission(_BaseModel):
    """Result of ``requests.batch``: one entry per submitted item, in order."""

    batch_id: str
    count: int
    accepted: int
    requests: list[BatchItemResult] = Field(default_factory=list)


# =============================================================================
# Account
# =============================================================================


class AgentTrial(_BaseModel):
    """The ``agent_trial`` block of ``account.get_account_info()`` for a trial key.

    Only present when the key is an agent trial key (minted without an
    account). Parse it with ``AgentTrial.model_validate(info["agent_trial"])``.

    Attributes:
        credits_remaining: Trial credits left.
        expires_at: When the trial key stops working (ISO-8601).
        claim_url: Link a human opens to move the key onto their account.
    """

    credits_remaining: int = 0
    expires_at: str | None = None
    claim_url: str | None = None
