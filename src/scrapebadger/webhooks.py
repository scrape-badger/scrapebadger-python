"""Receive ScrapeBadger async-request webhooks: verify the signature, parse the event.

A call submitted with a ``callback_url`` (``client.requests.submit(...,
callback_url=...)``, ``X-Callback-URL``, or a batch's ``callback_url``) gets one
``request.completed`` POST when it completes. Each delivery is signed with the
account's webhook secret (``client.account.webhook_secret()``):
``X-ScrapeBadger-Signature: sha256=<hex HMAC-SHA256 of the raw request body>``.

Example (FastAPI):
    ```python
    from fastapi import FastAPI, HTTPException, Request
    from scrapebadger.webhooks import parse_event, verify_signature

    app = FastAPI()

    @app.post("/hooks/scrapebadger")
    async def hook(request: Request) -> dict[str, bool]:
        raw = await request.body()  # the raw bytes, before any JSON parsing
        event = parse_event(raw)
        if not verify_signature(
            SECRET,
            raw,
            request.headers.get("X-ScrapeBadger-Signature", ""),
            sent_at=event.sent_at,
        ):
            raise HTTPException(401)
        # Deliveries can repeat: deduplicate on event.request_id.
        return {"ok": True}
    ```
"""

from __future__ import annotations

import hashlib
import hmac
import json
import math
import time
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

__all__ = ["SIGNATURE_HEADER", "WebhookEvent", "parse_event", "verify_signature"]

#: Header that carries the signature of a delivery.
SIGNATURE_HEADER = "X-ScrapeBadger-Signature"

_PREFIX = "sha256="


class WebhookEvent(BaseModel):
    """A ``request.completed`` webhook delivery.

    Attributes:
        event: Always "request.completed" today.
        request_id: The request that completed. Deliveries can repeat (retries),
            so deduplicate on it.
        batch_id: The batch the request belongs to, or None.
        status: The call's own HTTP status, errors included.
        headers: The call's response headers, lower-cased names.
        body: The call's response body: decoded JSON for a JSON response, else
            the text. None when ``body_omitted``.
        body_omitted: True when the body was over 1 MB and left out: fetch it
            from ``result_url`` before ``result_expires_at``.
        body_size: Size of the body in bytes.
        result_url: Where to read the result (``GET``, free) while it is kept.
        result_expires_at: Unix time the result stops being kept (about 15 min).
        attempt: Delivery attempt, 1 to 4.
        sent_at: Unix time this attempt was signed and sent. It is part of the
            signed body: pass it to ``verify_signature(..., sent_at=...)`` to
            reject replays.
    """

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="ignore")

    event: str = "request.completed"
    request_id: str
    batch_id: str | None = None
    status: int
    headers: dict[str, str] = Field(default_factory=dict)
    body: Any = None
    body_omitted: bool = False
    body_size: int | None = None
    result_url: str | None = None
    result_expires_at: int | None = None
    attempt: int = 1
    sent_at: int | None = None


def _as_bytes(value: bytes | bytearray | memoryview | str) -> bytes:
    if isinstance(value, str):
        return value.encode("utf-8")
    return bytes(value)


def verify_signature(
    secret: str,
    raw_body: bytes | bytearray | memoryview | str,
    signature: str | None,
    *,
    sent_at: float | str | None = None,
    tolerance_s: float = 300,
) -> bool:
    """Check that a webhook delivery is genuine (and, with ``sent_at``, fresh).

    Compares in constant time. Never raises on bad input: a missing or
    malformed signature, or an unreadable ``sent_at``, is simply invalid.

    Args:
        secret: The account's webhook secret (``client.account.webhook_secret()``).
        raw_body: The request body exactly as received. Re-serialised JSON will
            not match.
        signature: The ``X-ScrapeBadger-Signature`` header (``sha256=<hex>``).
        sent_at: The delivery's ``sent_at`` (Unix seconds). When given, a
            delivery older than ``tolerance_s`` (or that far in the future) is
            rejected. Take it from the parsed body (``parse_event(raw).sent_at``):
            the body is what is signed. The ``X-ScrapeBadger-Timestamp`` header
            carries the same value but is not itself signed.
        tolerance_s: Accepted age of ``sent_at`` in seconds (default 300).

    Returns:
        True when the signature matches (and ``sent_at`` is within tolerance).
    """
    if not secret or not signature:
        return False
    try:
        given = signature.strip().encode("ascii")
    except (AttributeError, UnicodeEncodeError):
        return False
    digest = hmac.new(secret.encode("utf-8"), _as_bytes(raw_body), hashlib.sha256).hexdigest()
    expected = (_PREFIX + digest).encode("ascii")
    if not hmac.compare_digest(expected, given):
        return False
    if sent_at is None:
        return True
    try:
        sent = float(sent_at)
    except (TypeError, ValueError):
        return False
    return math.isfinite(sent) and abs(time.time() - sent) <= tolerance_s


def parse_event(raw_body: bytes | bytearray | memoryview | str) -> WebhookEvent:
    """Parse a webhook delivery body into a ``WebhookEvent``.

    Parsing does not check authenticity: call ``verify_signature`` on the same
    raw body before acting on the event.

    Args:
        raw_body: The request body as received.

    Returns:
        The event.

    Raises:
        ValueError: The body is not JSON or not a ``request.completed`` payload
            (``pydantic.ValidationError`` is a ``ValueError``).
    """
    data = json.loads(_as_bytes(raw_body))
    if not isinstance(data, dict):
        msg = "A webhook body is a JSON object"
        raise ValueError(msg)
    return WebhookEvent.model_validate(data)
