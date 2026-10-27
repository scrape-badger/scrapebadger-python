"""Pydantic models for the agent platform endpoints.

Quote, feedback and async-request polling — the account-level helpers an
agent uses around the scraper APIs. None of these calls is ever billed. All
models are immutable (frozen) and ignore unknown fields for forward
compatibility.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


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
    """State of a call made with ``Prefer: respond-async``.

    Attributes:
        request_id: The request polled.
        running: True while the call is still in progress (HTTP 202). Poll
            again after ``retry_after_seconds``; never re-submit the call.
        status_code: HTTP status of this poll: 202 while running, otherwise
            the original call's status.
        retry_after_seconds: Suggested wait before the next poll (running only).
        result_id: ``X-Result-ID`` of the finished call, for free re-reads via
            ``results.get``.
        credits_used: ``X-Credits-Used`` of the finished call.
        data: The original call's response body once finished (any JSON
            value), or the 202 status body while running.
    """

    request_id: str
    running: bool
    status_code: int
    retry_after_seconds: int | None = None
    result_id: str | None = None
    credits_used: int | None = None
    data: Any = None


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
