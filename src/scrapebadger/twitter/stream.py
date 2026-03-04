"""StreamClient -- stream monitor management and WebSocket streaming.

Provides the StreamClient class for creating and managing Twitter stream
monitors, and for connecting to the live WebSocket event stream.
"""

from __future__ import annotations

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, AsyncIterator

from scrapebadger._internal.exceptions import WebSocketStreamError
from scrapebadger.twitter.stream_models import (
    BillingLogList,
    ConnectedEvent,
    DeliveryLogList,
    ErrorEvent,
    FilterRuleDeliveryLogList,
    FilterRulePricingTierList,
    FilterRuleQueryValidation,
    FilterRuleResponse,
    FilterRuleResponseList,
    PingEvent,
    StreamEvent,
    StreamEventType,
    StreamMonitor,
    StreamMonitorList,
    TweetEvent,
)

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient

logger = logging.getLogger(__name__)

# Minimum enforced reconnect delay regardless of caller configuration
_MIN_RECONNECT_DELAY_SECONDS = 5.0


def _ws_url_from_base(base_url: str) -> str:
    """Derive WebSocket URL from HTTP base URL.

    Replaces the scheme to produce a WebSocket URL:
    - 'https://...' becomes 'wss://...'
    - 'http://...'  becomes 'ws://...'

    Args:
        base_url: The HTTP(S) base URL from client config.

    Returns:
        The full WebSocket URL including the stream path.
    """
    if base_url.startswith("https://"):
        return base_url.replace("https://", "wss://", 1) + "/v1/twitter/stream"
    if base_url.startswith("http://"):
        return base_url.replace("http://", "ws://", 1) + "/v1/twitter/stream"
    return base_url + "/v1/twitter/stream"


def _parse_event(raw: dict[str, object]) -> StreamEvent:
    """Parse a raw JSON dict into a typed StreamEvent.

    Unknown event types are returned as ErrorEvent with code 0 so the caller
    is never left with an untyped raw dict.

    Args:
        raw: Parsed JSON dictionary from the WebSocket message.

    Returns:
        A typed StreamEvent (ConnectedEvent, PingEvent, TweetEvent, or ErrorEvent).
    """
    event_type = raw.get("type", "")
    if event_type == StreamEventType.CONNECTED:
        return ConnectedEvent.model_validate(raw)
    if event_type == StreamEventType.PING:
        return PingEvent.model_validate(raw)
    if event_type == StreamEventType.TWEET:
        return TweetEvent.model_validate(raw)
    if event_type == StreamEventType.ERROR:
        return ErrorEvent.model_validate(raw)
    return ErrorEvent(
        type=StreamEventType.ERROR,
        code=0,
        message=f"Unknown event type: {event_type!r}",
    )


def verify_webhook_signature(
    secret: str,
    body: str | bytes,
    signature_header: str,
) -> bool:
    """Verify an HMAC-SHA256 webhook signature from ScrapeBadger.

    Use this in your webhook receiver to ensure payloads are authentic.

    Example::

        import json
        from scrapebadger.twitter import verify_webhook_signature

        @app.post("/webhook")
        async def handle_webhook(request):
            sig = request.headers["x-scrapebadger-signature"]
            raw = await request.body()
            if not verify_webhook_signature("my-secret", raw, sig):
                return JSONResponse({"error": "Invalid signature"}, 401)
            event = json.loads(raw)
            # process event...

    Args:
        secret: The signing secret configured on the monitor.
        body: The raw request body (str or bytes).
        signature_header: The ``x-scrapebadger-signature`` header value
            (e.g. ``sha256=<hex>``).

    Returns:
        True if the signature is valid, False otherwise.
    """
    import hashlib
    import hmac

    if not signature_header.startswith("sha256="):
        return False

    expected_hex = signature_header[len("sha256="):]
    body_bytes = body.encode("utf-8") if isinstance(body, str) else body
    actual_hex = hmac.new(
        secret.encode("utf-8"),
        body_bytes,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected_hex, actual_hex)


class StreamClient:
    """Client for Twitter Streams -- monitor management and live tweet streaming.

    Accessed as ``client.twitter.stream``.

    Monitor CRUD example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            monitor = await client.twitter.stream.create_monitor(
                name="Elon Watch",
                usernames=["elonmusk", "naval"],
                poll_interval_seconds=5.0,
            )
            print(f"Created: {monitor.id}, tier: {monitor.pricing_tier}")

            monitors = await client.twitter.stream.list_monitors()
            for m in monitors.monitors:
                print(f"{m.name}: {m.status}")
        ```

    WebSocket streaming example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            async with client.twitter.stream.connect() as events:
                async for event in events:
                    if isinstance(event, TweetEvent):
                        print(f"@{event.author_username}: {event.tweet.text}")
                        print(f"  latency: {event.latency_ms}ms")
        ```

    The connect() context manager handles:
    - WebSocket connection and upgrade with x-api-key header authentication
    - Automatic pong responses to server pings (transparent to caller)
    - Graceful close on context exit
    - Optional auto-reconnect on unexpected disconnect
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize StreamClient.

        Args:
            client: The base HTTP client (provides api_key and base_url).
        """
        self._client = client

    # =========================================================================
    # Monitor CRUD
    # =========================================================================

    async def create_monitor(
        self,
        name: str,
        usernames: list[str],
        poll_interval_seconds: float,
        *,
        webhook_url: str | None = None,
        webhook_secret: str | None = None,
    ) -> StreamMonitor:
        """Create a new stream monitor.

        Args:
            name: Display name for the monitor (1-100 chars).
            usernames: Twitter handles to monitor (1-100 items). Leading '@'
                is stripped automatically by the server.
            poll_interval_seconds: Polling interval in seconds (>= 0.1).
                Determines the pricing tier.
            webhook_url: Optional HTTPS URL for webhook delivery.
            webhook_secret: Optional signing secret. Auto-generated by the
                server if webhook_url is set but secret is omitted.

        Returns:
            The created StreamMonitor.

        Raises:
            InsufficientCreditsError: If credit balance is below the tier
                threshold (HTTP 402).
            ValidationError: If any username is invalid or poll_interval_seconds
                is out of range (HTTP 422).
            ScrapeBadgerError: With status 409 if a monitor with that name
                already exists for this API key.
            AuthenticationError: If the API key is invalid (HTTP 401).

        Example:
            ```python
            monitor = await client.twitter.stream.create_monitor(
                name="Tech Leaders",
                usernames=["elonmusk", "naval", "sama"],
                poll_interval_seconds=10.0,
            )
            print(f"{monitor.id} -- tier: {monitor.pricing_tier}")
            ```
        """
        payload: dict[str, object] = {
            "name": name,
            "usernames": usernames,
            "poll_interval_seconds": poll_interval_seconds,
        }
        if webhook_url is not None:
            payload["webhook_url"] = webhook_url
        if webhook_secret is not None:
            payload["webhook_secret"] = webhook_secret

        data = await self._client.post("/v1/twitter/stream/monitors", json=payload)
        return StreamMonitor.model_validate(data)

    async def list_monitors(
        self,
        *,
        status: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> StreamMonitorList:
        """List stream monitors for the authenticated API key.

        Args:
            status: Filter by status ("active", "paused", or "error"). None
                returns all monitors.
            page: Page number (1-indexed).
            page_size: Results per page (1-100).

        Returns:
            StreamMonitorList with pagination metadata.

        Example:
            ```python
            result = await client.twitter.stream.list_monitors(status="active")
            print(f"Active monitors: {result.total}")
            for m in result.monitors:
                print(f"  {m.name}: {m.estimated_credits_per_hour:.1f} cr/hr")
            ```
        """
        params: dict[str, object] = {"page": page, "page_size": page_size}
        if status is not None:
            params["status"] = status
        data = await self._client.get("/v1/twitter/stream/monitors", params=params)
        return StreamMonitorList.model_validate(data)

    async def get_monitor(self, monitor_id: str) -> StreamMonitor:
        """Get a single stream monitor by ID.

        Args:
            monitor_id: UUID of the monitor.

        Returns:
            The StreamMonitor.

        Raises:
            NotFoundError: If no monitor exists with that ID for this API key.

        Example:
            ```python
            monitor = await client.twitter.stream.get_monitor("550e8400-...")
            print(f"{monitor.name}: {monitor.status}")
            ```
        """
        data = await self._client.get(f"/v1/twitter/stream/monitors/{monitor_id}")
        return StreamMonitor.model_validate(data)

    async def update_monitor(
        self,
        monitor_id: str,
        *,
        name: str | None = None,
        usernames: list[str] | None = None,
        poll_interval_seconds: float | None = None,
        status: str | None = None,
        webhook_url: str | None = None,
        webhook_secret: str | None = None,
    ) -> StreamMonitor:
        """Partially update a stream monitor.

        Only fields that are explicitly passed (not None) are sent to the
        server. Fields left as None are left unchanged.

        Args:
            monitor_id: UUID of the monitor to update.
            name: New display name.
            usernames: Replacement list of Twitter handles.
            poll_interval_seconds: New polling interval.
            status: New status. Only "active" or "paused" are valid.
            webhook_url: New webhook URL (empty string clears it).
            webhook_secret: New webhook signing secret.

        Returns:
            The updated StreamMonitor.

        Raises:
            NotFoundError: If the monitor does not exist for this API key.
            InsufficientCreditsError: When resuming or lowering the interval
                with insufficient credits.

        Example:
            ```python
            monitor = await client.twitter.stream.update_monitor(
                "550e8400-...",
                poll_interval_seconds=60.0,
            )
            print(f"New tier: {monitor.pricing_tier}")
            ```
        """
        payload: dict[str, object] = {}
        if name is not None:
            payload["name"] = name
        if usernames is not None:
            payload["usernames"] = usernames
        if poll_interval_seconds is not None:
            payload["poll_interval_seconds"] = poll_interval_seconds
        if status is not None:
            payload["status"] = status
        if webhook_url is not None:
            payload["webhook_url"] = webhook_url
        if webhook_secret is not None:
            payload["webhook_secret"] = webhook_secret

        data = await self._client._request(
            "PATCH",
            f"/v1/twitter/stream/monitors/{monitor_id}",
            json=payload,
        )
        return StreamMonitor.model_validate(data)

    async def pause_monitor(self, monitor_id: str) -> StreamMonitor:
        """Pause an active stream monitor.

        Convenience wrapper around update_monitor(status="paused").

        Args:
            monitor_id: UUID of the monitor.

        Returns:
            The updated StreamMonitor with status="paused".

        Example:
            ```python
            monitor = await client.twitter.stream.pause_monitor("550e8400-...")
            assert monitor.status == MonitorStatus.PAUSED
            ```
        """
        return await self.update_monitor(monitor_id, status="paused")

    async def resume_monitor(self, monitor_id: str) -> StreamMonitor:
        """Resume a paused stream monitor.

        Convenience wrapper around update_monitor(status="active").

        Args:
            monitor_id: UUID of the monitor.

        Returns:
            The updated StreamMonitor with status="active".

        Raises:
            InsufficientCreditsError: If credit balance is below the tier
                threshold required to resume.

        Example:
            ```python
            monitor = await client.twitter.stream.resume_monitor("550e8400-...")
            assert monitor.status == MonitorStatus.ACTIVE
            ```
        """
        return await self.update_monitor(monitor_id, status="active")

    async def delete_monitor(self, monitor_id: str) -> None:
        """Delete a stream monitor and all its associated logs.

        This action is irreversible. The server returns HTTP 204 with no body.

        Args:
            monitor_id: UUID of the monitor to delete.

        Raises:
            NotFoundError: If the monitor does not exist for this API key.

        Example:
            ```python
            await client.twitter.stream.delete_monitor("550e8400-...")
            ```
        """
        await self._client._request(
            "DELETE",
            f"/v1/twitter/stream/monitors/{monitor_id}",
        )

    # =========================================================================
    # Delivery and Billing Logs
    # =========================================================================

    async def list_delivery_logs(
        self,
        *,
        monitor_id: str | None = None,
        author_username: str | None = None,
        delivery_status: str | None = None,
        page: int = 1,
        page_size: int = 20,
        sort: str = "desc",
    ) -> DeliveryLogList:
        """List tweet delivery logs.

        Args:
            monitor_id: Filter to a specific monitor.
            author_username: Filter to a specific author handle.
            delivery_status: Filter by status ("websocket_delivered",
                "webhook_delivered", "webhook_failed").
            page: Page number (1-indexed).
            page_size: Results per page (1-100).
            sort: Sort direction ("asc" or "desc").

        Returns:
            DeliveryLogList with pagination metadata.

        Example:
            ```python
            logs = await client.twitter.stream.list_delivery_logs(
                monitor_id="550e8400-...",
                page_size=50,
            )
            print(f"Total deliveries: {logs.total}")
            ```
        """
        params: dict[str, object] = {"page": page, "page_size": page_size, "sort": sort}
        if monitor_id is not None:
            params["monitor_id"] = monitor_id
        if author_username is not None:
            params["author_username"] = author_username
        if delivery_status is not None:
            params["delivery_status"] = delivery_status
        data = await self._client.get("/v1/twitter/stream/logs", params=params)
        return DeliveryLogList.model_validate(data)

    async def list_billing_logs(
        self,
        *,
        monitor_id: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> BillingLogList:
        """List billing activity logs.

        Args:
            monitor_id: Filter to a specific monitor.
            page: Page number (1-indexed).
            page_size: Results per page (1-100).

        Returns:
            BillingLogList with pagination metadata.

        Example:
            ```python
            billing = await client.twitter.stream.list_billing_logs()
            for log in billing.logs:
                print(f"{log.monitor_name}: -{log.credits_deducted} credits")
            ```
        """
        params: dict[str, object] = {"page": page, "page_size": page_size}
        if monitor_id is not None:
            params["monitor_id"] = monitor_id
        data = await self._client.get("/v1/twitter/stream/billing-logs", params=params)
        return BillingLogList.model_validate(data)

    # =========================================================================
    # Filter Rules
    # =========================================================================

    async def create_filter_rule(
        self,
        tag: str,
        query: str,
        interval_seconds: float,
        *,
        webhook_url: str | None = None,
        webhook_secret: str | None = None,
        max_results_per_poll: int | None = None,
    ) -> FilterRuleResponse:
        """Create a new filter rule.

        Filter rules monitor a Twitter search query and deliver matching tweets
        on a configurable polling interval.

        Args:
            tag: Human-readable label for the rule (used in logs and webhooks).
            query: Twitter advanced search query string (e.g.
                ``"#python lang:en -is:retweet"``).
            interval_seconds: Polling interval in seconds. Determines the
                pricing tier.
            webhook_url: Optional HTTPS URL for webhook delivery.
            webhook_secret: Optional signing secret for HMAC-SHA256 webhook
                verification. Auto-generated by the server if webhook_url is
                set but secret is omitted.
            max_results_per_poll: Maximum tweets to fetch per polling cycle.
                Server default applies when None.

        Returns:
            The created FilterRuleResponse.

        Raises:
            InsufficientCreditsError: If credit balance is below the tier
                threshold (HTTP 402).
            ValidationError: If the query is invalid or interval_seconds is
                out of range (HTTP 422).
            AuthenticationError: If the API key is invalid (HTTP 401).

        Example:
            ```python
            rule = await client.twitter.stream.create_filter_rule(
                tag="Python news",
                query="#python lang:en -is:retweet",
                interval_seconds=60.0,
            )
            print(f"{rule.id} -- tier: {rule.pricing_tier}")
            ```
        """
        payload: dict[str, object] = {
            "tag": tag,
            "query": query,
            "interval_seconds": interval_seconds,
        }
        if webhook_url is not None:
            payload["webhook_url"] = webhook_url
        if webhook_secret is not None:
            payload["webhook_secret"] = webhook_secret
        if max_results_per_poll is not None:
            payload["max_results_per_poll"] = max_results_per_poll

        data = await self._client.post("/v1/twitter/stream/filter-rules", json=payload)
        return FilterRuleResponse.model_validate(data)

    async def list_filter_rules(
        self,
        *,
        status: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> FilterRuleResponseList:
        """List filter rules for the authenticated API key.

        Args:
            status: Filter by status ("active", "paused", "error", or
                "inactive"). None returns all rules.
            limit: Maximum results to return (default 20).
            offset: Number of results to skip for pagination (default 0).

        Returns:
            FilterRuleResponseList with pagination metadata.

        Example:
            ```python
            result = await client.twitter.stream.list_filter_rules(status="active")
            print(f"Active rules: {result.total}")
            for rule in result.rules:
                print(f"  {rule.tag}: {rule.credits_per_rule_per_day:.1f} cr/day")
            ```
        """
        params: dict[str, object] = {"limit": limit, "offset": offset}
        if status is not None:
            params["status"] = status
        data = await self._client.get("/v1/twitter/stream/filter-rules", params=params)
        return FilterRuleResponseList.model_validate(data)

    async def get_filter_rule(self, rule_id: str) -> FilterRuleResponse:
        """Get a single filter rule by ID.

        Args:
            rule_id: UUID of the filter rule.

        Returns:
            The FilterRuleResponse.

        Raises:
            NotFoundError: If no rule exists with that ID for this API key.

        Example:
            ```python
            rule = await client.twitter.stream.get_filter_rule("550e8400-...")
            print(f"{rule.tag}: {rule.status}")
            ```
        """
        data = await self._client.get(f"/v1/twitter/stream/filter-rules/{rule_id}")
        return FilterRuleResponse.model_validate(data)

    async def update_filter_rule(
        self,
        rule_id: str,
        *,
        tag: str | None = None,
        query: str | None = None,
        interval_seconds: float | None = None,
        status: str | None = None,
        webhook_url: str | None = None,
        webhook_secret: str | None = None,
        max_results_per_poll: int | None = None,
    ) -> FilterRuleResponse:
        """Partially update a filter rule.

        Only fields that are explicitly passed (not None) are sent to the
        server. Fields left as None are left unchanged.

        Args:
            rule_id: UUID of the filter rule to update.
            tag: New human-readable label.
            query: New Twitter search query string.
            interval_seconds: New polling interval.
            status: New status. Only "active" or "paused" are valid.
            webhook_url: New webhook URL (empty string clears it).
            webhook_secret: New webhook signing secret.
            max_results_per_poll: New maximum results per polling cycle.

        Returns:
            The updated FilterRuleResponse.

        Raises:
            NotFoundError: If the rule does not exist for this API key.
            InsufficientCreditsError: When resuming or lowering the interval
                with insufficient credits.

        Example:
            ```python
            rule = await client.twitter.stream.update_filter_rule(
                "550e8400-...",
                interval_seconds=300.0,
            )
            print(f"New tier: {rule.pricing_tier}")
            ```
        """
        payload: dict[str, object] = {}
        if tag is not None:
            payload["tag"] = tag
        if query is not None:
            payload["query"] = query
        if interval_seconds is not None:
            payload["interval_seconds"] = interval_seconds
        if status is not None:
            payload["status"] = status
        if webhook_url is not None:
            payload["webhook_url"] = webhook_url
        if webhook_secret is not None:
            payload["webhook_secret"] = webhook_secret
        if max_results_per_poll is not None:
            payload["max_results_per_poll"] = max_results_per_poll

        data = await self._client._request(
            "PATCH",
            f"/v1/twitter/stream/filter-rules/{rule_id}",
            json=payload,
        )
        return FilterRuleResponse.model_validate(data)

    async def delete_filter_rule(self, rule_id: str) -> None:
        """Delete a filter rule and all its associated logs.

        This action is irreversible.

        Args:
            rule_id: UUID of the filter rule to delete.

        Raises:
            NotFoundError: If the rule does not exist for this API key.

        Example:
            ```python
            await client.twitter.stream.delete_filter_rule("550e8400-...")
            ```
        """
        await self._client._request(
            "DELETE",
            f"/v1/twitter/stream/filter-rules/{rule_id}",
        )

    async def pause_filter_rule(self, rule_id: str) -> FilterRuleResponse:
        """Pause an active filter rule.

        Convenience wrapper around update_filter_rule(status="paused").

        Args:
            rule_id: UUID of the filter rule.

        Returns:
            The updated FilterRuleResponse with status="paused".

        Example:
            ```python
            rule = await client.twitter.stream.pause_filter_rule("550e8400-...")
            assert rule.status == FilterRuleStatus.PAUSED
            ```
        """
        return await self.update_filter_rule(rule_id, status="paused")

    async def resume_filter_rule(self, rule_id: str) -> FilterRuleResponse:
        """Resume a paused filter rule.

        Convenience wrapper around update_filter_rule(status="active").

        Args:
            rule_id: UUID of the filter rule.

        Returns:
            The updated FilterRuleResponse with status="active".

        Raises:
            InsufficientCreditsError: If credit balance is below the tier
                threshold required to resume.

        Example:
            ```python
            rule = await client.twitter.stream.resume_filter_rule("550e8400-...")
            assert rule.status == FilterRuleStatus.ACTIVE
            ```
        """
        return await self.update_filter_rule(rule_id, status="active")

    async def validate_filter_rule_query(
        self,
        query: str,
    ) -> FilterRuleQueryValidation:
        """Validate a Twitter search query string before creating a filter rule.

        Sends the query to the server for syntax validation and a lightweight
        sample check against recent tweets.

        Args:
            query: Twitter advanced search query string to validate.

        Returns:
            FilterRuleQueryValidation with valid=True on success or an error
            message if the query is invalid.

        Example:
            ```python
            result = await client.twitter.stream.validate_filter_rule_query(
                "#python lang:en -is:retweet"
            )
            if result.valid:
                print(f"Query OK, {result.sample_results} sample tweets found")
            else:
                print(f"Bad query: {result.error}")
            ```
        """
        data = await self._client.post(
            "/v1/twitter/stream/filter-rules/validate",
            json={"query": query},
        )
        return FilterRuleQueryValidation.model_validate(data)

    async def list_filter_rule_delivery_logs(
        self,
        rule_id: str,
        *,
        limit: int = 20,
        offset: int = 0,
        delivery_status: str | None = None,
        sort: str = "desc",
    ) -> FilterRuleDeliveryLogList:
        """List tweet delivery logs for a specific filter rule.

        Args:
            rule_id: UUID of the filter rule.
            limit: Maximum results to return (default 20).
            offset: Number of results to skip for pagination (default 0).
            delivery_status: Filter by delivery outcome. None returns all.
            sort: Sort direction ("asc" or "desc").

        Returns:
            FilterRuleDeliveryLogList with pagination metadata.

        Example:
            ```python
            logs = await client.twitter.stream.list_filter_rule_delivery_logs(
                "550e8400-...",
                limit=50,
            )
            print(f"Total deliveries: {logs.total}")
            ```
        """
        params: dict[str, object] = {
            "limit": limit,
            "offset": offset,
            "sort": sort,
        }
        if delivery_status is not None:
            params["delivery_status"] = delivery_status

        data = await self._client.get(
            f"/v1/twitter/stream/filter-rules/{rule_id}/logs",
            params=params,
        )
        return FilterRuleDeliveryLogList.model_validate(data)

    async def get_filter_rule_pricing(self) -> FilterRulePricingTierList:
        """Get available pricing tiers for filter rules.

        Returns the full list of pricing tiers ordered by display_order,
        from fastest/most expensive to slowest/cheapest.

        Returns:
            FilterRulePricingTierList containing all configured tiers.

        Example:
            ```python
            pricing = await client.twitter.stream.get_filter_rule_pricing()
            for tier in pricing.tiers:
                print(
                    f"{tier.tier_label}: "
                    f"up to every {tier.max_interval_seconds}s "
                    f"= {tier.credits_per_rule_per_day} cr/day"
                )
            ```
        """
        data = await self._client.get("/v1/twitter/stream/filter-rules-pricing")
        return FilterRulePricingTierList.model_validate(data)

    # =========================================================================
    # WebSocket Streaming
    # =========================================================================

    @asynccontextmanager
    async def connect(
        self,
        *,
        reconnect: bool = False,
        reconnect_delay_seconds: float = 90.0,
        max_reconnects: int | None = None,
    ) -> AsyncIterator[AsyncIterator[StreamEvent]]:
        """Connect to the WebSocket stream and yield tweet events.

        This is an async context manager that yields an async iterator of
        StreamEvent objects. The context manager handles:
        - WebSocket handshake with x-api-key header authentication
        - Automatic pong responses to server pings (transparent to caller)
        - Graceful close on context exit
        - Optional auto-reconnect on unexpected disconnect

        When reconnect=False (default), the iterator raises
        WebSocketStreamError on any disconnect.

        When reconnect=True, the iterator silently reconnects (after the
        configured delay) and continues yielding events. ConnectedEvent is
        yielded on each successful (re)connect so the caller can detect
        reconnections.

        Args:
            reconnect: If True, automatically reconnect on disconnect.
            reconnect_delay_seconds: Minimum seconds to wait between reconnect
                attempts. Enforced floor of 5 seconds.
            max_reconnects: Maximum number of reconnect attempts. None means
                unlimited. Exhausted attempts raise WebSocketStreamError.

        Yields:
            AsyncIterator[StreamEvent]: Async iterator of stream events.

        Raises:
            WebSocketStreamError: On auth failure (code 4001), connection
                limit exceeded (code 4003), or unexpected disconnect when
                reconnect=False.
            WebSocketStreamError: When max_reconnects is exhausted.

        Example:
            ```python
            # Simple: receive tweets until disconnect
            async with client.twitter.stream.connect() as events:
                async for event in events:
                    if isinstance(event, TweetEvent):
                        print(f"{event.author_username}: {event.latency_ms}ms")

            # With auto-reconnect
            async with client.twitter.stream.connect(
                reconnect=True,
                reconnect_delay_seconds=90.0,
            ) as events:
                async for event in events:
                    if isinstance(event, TweetEvent):
                        process(event)
            ```
        """
        import websockets
        from websockets.exceptions import ConnectionClosed

        delay = max(_MIN_RECONNECT_DELAY_SECONDS, reconnect_delay_seconds)
        ws_url = _ws_url_from_base(self._client.config.base_url)
        api_key = self._client.config.api_key
        reconnect_count = 0

        async def _event_generator() -> AsyncIterator[StreamEvent]:
            nonlocal reconnect_count

            while True:
                try:
                    async with websockets.connect(
                        ws_url,
                        additional_headers={"x-api-key": api_key},
                        ping_interval=None,  # Disable library-level ping; server sends its own
                        ping_timeout=None,
                    ) as ws:
                        async for raw_text in ws:
                            try:
                                raw: dict[str, object] = json.loads(raw_text)
                            except json.JSONDecodeError:
                                logger.warning("Received non-JSON WebSocket message; skipping")
                                continue

                            event = _parse_event(raw)

                            # Handle ping transparently -- respond and yield to caller
                            if isinstance(event, PingEvent):
                                await ws.send(json.dumps({"type": "pong"}))
                                yield event
                                continue

                            # Auth/limit errors: raise immediately, do not reconnect
                            if isinstance(event, ErrorEvent) and event.code in (4001, 4003):
                                raise WebSocketStreamError(event.message, code=event.code)

                            yield event

                except ConnectionClosed as exc:
                    if not reconnect:
                        raise WebSocketStreamError(
                            f"WebSocket closed unexpectedly: {exc}",
                        ) from exc

                    if max_reconnects is not None and reconnect_count >= max_reconnects:
                        raise WebSocketStreamError(
                            f"Max reconnects ({max_reconnects}) exhausted",
                        ) from exc

                    reconnect_count += 1
                    logger.info(
                        "WebSocket disconnected, reconnecting in %.1fs (attempt %d)",
                        delay,
                        reconnect_count,
                    )
                    await asyncio.sleep(delay)
                    # Loop continues: new connection on next iteration

                except WebSocketStreamError:
                    raise  # Auth/limit errors are not retried

                else:
                    # Clean server close: do not reconnect unless asked
                    if not reconnect:
                        return
                    if max_reconnects is not None and reconnect_count >= max_reconnects:
                        raise WebSocketStreamError("Max reconnects exhausted")
                    reconnect_count += 1
                    await asyncio.sleep(delay)

        yield _event_generator()
