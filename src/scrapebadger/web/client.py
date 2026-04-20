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
            raw_content: When True, the server streams the raw body as
                text/html with metadata in ``X-Scrape-*`` response headers
                instead of JSON-wrapping the content. Saves 300-1000 ms on
                large (>1 MB) pages. Incompatible with ``ai_extract``,
                ``screenshot``, ``video``.
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

        response = await self._client.post("/v1/web/scrape", json=body)
        return ScrapeResult.model_validate(response)

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
