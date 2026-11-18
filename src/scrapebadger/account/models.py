"""Pydantic models for the account endpoints: webhook secret and deliveries.

All models are immutable (frozen) and ignore unknown fields for forward
compatibility.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class _BaseModel(BaseModel):
    """Base model with common configuration."""

    model_config = ConfigDict(
        frozen=True,
        populate_by_name=True,
        extra="ignore",
    )


class WebhookSecret(_BaseModel):
    """The secret that signs every webhook of the account.

    Pass ``secret`` to ``scrapebadger.webhooks.verify_signature``.

    Attributes:
        secret: The signing secret (``whsec_...``). Treat it like a password.
        signature_header: Header that carries the signature.
        algorithm: How the signature is made.
    """

    secret: str
    signature_header: str = "X-ScrapeBadger-Signature"
    algorithm: str = "sha256=<hex HMAC-SHA256 of the raw request body>"


class WebhookDelivery(_BaseModel):
    """One webhook delivery of the last 24 hours.

    Only metadata is kept: the endpoint path (never its query) and the
    callback host (never its path or query), statuses, attempts and times.

    Attributes:
        request_id: The request the webhook is for.
        endpoint: Path of the call, e.g. "/v1/perplexity/ask".
        state: "pending", "delivering", "delivered" or "failed".
        attempts: Attempts made so far.
        last_status: HTTP status your endpoint answered on the last attempt.
        last_error: Short error class of the last attempt.
        created_at: Unix time the delivery was scheduled.
        delivered_at: Unix time it was delivered, or None.
        callback_host: Host of the callback URL.
    """

    request_id: str
    endpoint: str | None = None
    state: str = "pending"
    attempts: int = 0
    last_status: int | None = None
    last_error: str | None = None
    created_at: int | float | None = None
    delivered_at: int | float | None = None
    callback_host: str | None = None


class WebhookDeliveries(_BaseModel):
    """The account's webhook deliveries, newest first.

    Attributes:
        deliveries: The deliveries.
        window_hours: How far back the list goes (24).
    """

    deliveries: list[WebhookDelivery] = Field(default_factory=list)
    window_hours: int = 24
