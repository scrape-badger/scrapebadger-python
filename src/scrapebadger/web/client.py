"""Web scraping API client for ScrapeBadger SDK."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.web.models import DetectResult, ScrapeResult

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class WebClient:
    """Client for web scraping operations.

    Provides async methods for scraping web pages, extracting data with AI,
    and detecting anti-bot systems.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            # Simple scrape
            result = await client.web.scrape("https://scrapebadger.com")
            print(result.content)

            # Scrape with JavaScript rendering
            result = await client.web.scrape(
                "https://scrapebadger.com",
                render_js=True,
                format="markdown",
            )

            # AI extraction
            result = await client.web.extract(
                "https://scrapebadger.com",
                prompt="Extract the main heading and description",
            )
            print(result.ai_extraction)

            # Anti-bot detection
            detection = await client.web.detect("https://scrapebadger.com")
            print(detection.antibot_systems)
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        self._client = client

    async def scrape(
        self,
        url: str,
        *,
        format: str = "html",
        render_js: bool = False,
        engine: str | None = None,
        wait_for: str | None = None,
        wait_timeout: int | None = None,
        wait_after_load: int | None = None,
        js_scenario: list[dict[str, Any]] | None = None,
        session_id: str | None = None,
        retry_count: int | None = None,
        retry_on_block: bool | None = None,
        country: str | None = None,
        custom_headers: dict[str, str] | None = None,
        screenshot: bool = False,
        video: bool = False,
        anti_bot: bool = False,
        escalate: bool = False,
        max_cost: int | None = None,
        ai_extract: bool = False,
        ai_prompt: str | None = None,
        raw_content: bool = False,
        skip_bot_detection: bool = False,
    ) -> ScrapeResult:
        """Scrape a web page.

        Args:
            url: URL to scrape.
            format: Output format (html, markdown, text, json).
            render_js: Whether to render JavaScript.
            engine: Force a specific engine.
            wait_for: CSS selector to wait for.
            wait_timeout: Maximum wait time in milliseconds.
            wait_after_load: Delay after page load in milliseconds.
            js_scenario: JavaScript actions to execute.
            session_id: Reuse an existing session.
            retry_count: Number of retries on failure.
            retry_on_block: Whether to retry when blocking is detected.
            country: Country code for proxy (e.g. "US").
            custom_headers: Custom HTTP headers to send.
            screenshot: Whether to capture a screenshot.
            video: Whether to record a video.
            anti_bot: Whether to enable anti-bot solving.
            escalate: Whether to escalate to more powerful engines on failure.
            max_cost: Maximum credit cost.
            ai_extract: Whether to enable AI data extraction.
            ai_prompt: Prompt for AI extraction.
            raw_content: When True, the server returns the body itself
                rather than a JSON envelope, with metadata in ``X-Scrape-*``
                response headers. The body lands in ``ScrapeResult.content_bytes``
                (and in ``content`` too when it is text). Saves 300-1000 ms on
                large (>1 MB) pages, and is the cheapest way to download a
                binary file — no base64 expansion. Incompatible with
                ``ai_extract``, ``screenshot``, ``video``.
            skip_bot_detection: When True, the server skips the generic
                blocking-page + anti-bot / CAPTCHA regex scans on the
                response body. Saves ~1.3 s of regex work on large pages.
                Only safe for origins that don't use consumer WAFs like
                Cloudflare / DataDome / Akamai / Kasada. Default False —
                keep enabled for general-purpose scraping.

        Returns:
            ScrapeResult with page content and metadata.
        """
        body: dict[str, Any] = {"url": url}
        if format != "html":
            body["format"] = format
        if render_js:
            body["render_js"] = True
        if engine is not None:
            body["engine"] = engine
        if wait_for is not None:
            body["wait_for"] = wait_for
        if wait_timeout is not None:
            body["wait_timeout"] = wait_timeout
        if wait_after_load is not None:
            body["wait_after_load"] = wait_after_load
        if js_scenario is not None:
            body["js_scenario"] = js_scenario
        if session_id is not None:
            body["session_id"] = session_id
        if retry_count is not None:
            body["retry_count"] = retry_count
        if retry_on_block is not None:
            body["retry_on_block"] = retry_on_block
        if country is not None:
            body["country"] = country
        if custom_headers is not None:
            body["custom_headers"] = custom_headers
        if screenshot:
            body["screenshot"] = True
        if video:
            body["video"] = True
        if anti_bot:
            body["anti_bot"] = True
        if escalate:
            body["escalate"] = True
        if max_cost is not None:
            body["max_cost"] = max_cost
        if ai_extract:
            body["ai_extract"] = True
        if ai_prompt is not None:
            body["ai_prompt"] = ai_prompt
        if raw_content:
            body["raw_content"] = True
        if skip_bot_detection:
            body["skip_bot_detection"] = True

        if raw_content:
            return await self._scrape_raw(body)

        response = await self._client.post("/v1/web/scrape", json=body)
        return ScrapeResult.model_validate(response)

    async def _scrape_raw(self, body: dict[str, Any]) -> ScrapeResult:
        """Run a ``raw_content`` scrape, whose response is not JSON.

        The normal path calls ``response.json()`` and falls back to ``{}``, so
        every ``raw_content=True`` scrape used to return an empty ScrapeResult
        with no error at all. Read the body as bytes and rebuild the metadata
        from the ``X-Scrape-*`` headers the server sends in this mode.
        """
        payload, headers, status_code = await self._client.post_raw("/v1/web/scrape", json=body)
        lower = {k.lower(): v for k, v in headers.items()}

        def _int(name: str) -> int:
            try:
                return int(lower.get(name, "0"))
            except (TypeError, ValueError):
                return 0

        content_type = lower.get("content-type", "")
        media_type = content_type.split(";", 1)[0].strip().lower()
        # Only decode when the payload is genuinely text — decoding an image or
        # a PDF is the very corruption this mode exists to avoid.
        is_text = media_type.startswith("text/") or media_type in {
            "application/json",
            "application/xml",
            "image/svg+xml",
        }

        return ScrapeResult(
            success=lower.get("x-scrape-success", "1") == "1",
            url=lower.get("x-scrape-url", str(body.get("url", ""))),
            status_code=_int("x-scrape-status-code") or status_code,
            content=payload.decode("utf-8", errors="replace") if is_text else None,
            content_bytes=payload,
            is_binary=not is_text,
            content_type=media_type or None,
            format=lower.get("x-scrape-format", "html"),
            engine_used=lower.get("x-scrape-engine"),
            credits_used=_int("x-credits-used"),
            duration_ms=_int("x-scrape-duration-ms"),
            retries_used=_int("x-scrape-retries"),
            content_length=_int("x-scrape-content-length") or len(payload),
        )

    async def extract(
        self,
        url: str,
        prompt: str,
        *,
        format: str = "markdown",
        render_js: bool = False,
        engine: str | None = None,
        wait_for: str | None = None,
        wait_timeout: int | None = None,
        wait_after_load: int | None = None,
        js_scenario: list[dict[str, Any]] | None = None,
        session_id: str | None = None,
        retry_count: int | None = None,
        retry_on_block: bool | None = None,
        country: str | None = None,
        custom_headers: dict[str, str] | None = None,
        screenshot: bool = False,
        video: bool = False,
        anti_bot: bool = False,
        escalate: bool = False,
        max_cost: int | None = None,
    ) -> ScrapeResult:
        """Extract structured data from a web page using AI.

        Convenience wrapper around scrape() with ai_extract=True.

        Args:
            url: URL to extract from.
            prompt: AI extraction prompt describing what to extract.
            format: Output format (html, markdown, text, json).
            render_js: Whether to render JavaScript.
            engine: Force a specific engine.
            wait_for: CSS selector to wait for.
            wait_timeout: Maximum wait time in milliseconds.
            wait_after_load: Delay after page load in milliseconds.
            js_scenario: JavaScript actions to execute.
            session_id: Reuse an existing session.
            retry_count: Number of retries on failure.
            retry_on_block: Whether to retry when blocking is detected.
            country: Country code for proxy (e.g. "US").
            custom_headers: Custom HTTP headers to send.
            screenshot: Whether to capture a screenshot.
            video: Whether to record a video.
            anti_bot: Whether to enable anti-bot solving.
            escalate: Whether to escalate to more powerful engines on failure.
            max_cost: Maximum credit cost.

        Returns:
            ScrapeResult with ai_extraction field containing extracted data.
        """
        return await self.scrape(
            url,
            format=format,
            render_js=render_js,
            engine=engine,
            wait_for=wait_for,
            wait_timeout=wait_timeout,
            wait_after_load=wait_after_load,
            js_scenario=js_scenario,
            session_id=session_id,
            retry_count=retry_count,
            retry_on_block=retry_on_block,
            country=country,
            custom_headers=custom_headers,
            screenshot=screenshot,
            video=video,
            anti_bot=anti_bot,
            escalate=escalate,
            max_cost=max_cost,
            ai_extract=True,
            ai_prompt=prompt,
        )

    async def detect(
        self,
        url: str,
        *,
        timeout: int | None = None,
        country: str | None = None,
    ) -> DetectResult:
        """Detect anti-bot systems on a web page.

        Args:
            url: URL to detect anti-bot systems on.
            timeout: Request timeout in milliseconds.
            country: Country code for proxy (e.g. "US").

        Returns:
            DetectResult with detected anti-bot and captcha systems.
        """
        body: dict[str, Any] = {"url": url}
        if timeout is not None:
            body["timeout"] = timeout
        if country is not None:
            body["country"] = country

        response = await self._client.post("/v1/web/detect", json=body)
        return DetectResult.model_validate(response)

    # --- generated by sdk/codegen/facade — do not edit ---

    async def submit_batch_scraping_job(
        self, *, payload: dict[str, Any] | None = None, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Submit batch scraping job.

        Generated from the OpenAPI spec; returns the raw response dict.
        """
        return await self._client.post("/v1/web/batch", params=params, json=payload)

    async def get_batch_job_status(self, job_id: str) -> dict[str, Any]:
        """Get batch job status.

        Generated from the OpenAPI spec; returns the raw response dict.
        """
        return await self._client.get(f"/v1/web/batch/{job_id}")

    async def extract_structured_data(
        self, *, payload: dict[str, Any] | None = None, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Extract structured data.

        Generated from the OpenAPI spec; returns the raw response dict.
        """
        return await self._client.post("/v1/web/extract", params=params, json=payload)

    async def take_a_screenshot(
        self, *, payload: dict[str, Any] | None = None, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Take a screenshot.

        Generated from the OpenAPI spec; returns the raw response dict.
        """
        return await self._client.post("/v1/web/screenshot", params=params, json=payload)

    async def poll_an_auto_unblock_discovery_job(self, job_id: str) -> dict[str, Any]:
        """Poll an auto-unblock discovery job.

        Generated from the OpenAPI spec; returns the raw response dict.
        """
        return await self._client.get(f"/v1/web/unblock/{job_id}")
