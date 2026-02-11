"""Web scraping API client for ScrapeBadger SDK."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.web.models import (
    BatchResult,
    ExtractResult,
    ScrapeResult,
    ScreenshotResult,
    SessionInfo,
)

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class WebClient:
    """Client for web scraping operations.

    Provides async methods for scraping web pages, taking screenshots,
    extracting structured data, and managing scraping sessions.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            # Simple scrape
            result = await client.web.scrape("https://example.com")
            print(result.content)

            # Screenshot
            screenshot = await client.web.screenshot("https://example.com")

            # Extract data
            data = await client.web.extract(
                "https://example.com",
                schema={"title": "css:h1"}
            )

            # Batch scrape
            batch = await client.web.batch(["https://a.com", "https://b.com"])
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        self._client = client

    async def scrape(
        self,
        url: str,
        *,
        render_js: bool = False,
        output_format: str = "html",
        proxy_country: str | None = None,
        proxy_type: str | None = None,
        session_id: str | None = None,
        engine: str | None = None,
        max_cost: int | None = None,
        headers: dict[str, str] | None = None,
        wait_for: str | None = None,
        timeout: float | None = None,
        js_scenario: list[dict[str, Any]] | None = None,
    ) -> ScrapeResult:
        """Scrape a web page.

        Args:
            url: URL to scrape.
            render_js: Whether to render JavaScript.
            output_format: Output format (html, markdown, text, json).
            proxy_country: Country code for proxy (e.g. "US").
            proxy_type: Proxy type (datacenter, residential).
            session_id: Reuse an existing session.
            engine: Force a specific engine.
            max_cost: Maximum credit cost.
            headers: Custom HTTP headers.
            wait_for: CSS selector to wait for.
            timeout: Request timeout in seconds.
            js_scenario: JavaScript actions to execute.

        Returns:
            ScrapeResult with page content and metadata.
        """
        body: dict[str, Any] = {"url": url}
        if render_js:
            body["render_js"] = True
        if output_format != "html":
            body["output_format"] = output_format
        if proxy_country is not None:
            body["proxy_country"] = proxy_country
        if proxy_type is not None:
            body["proxy_type"] = proxy_type
        if session_id is not None:
            body["session_id"] = session_id
        if engine is not None:
            body["engine"] = engine
        if max_cost is not None:
            body["max_cost"] = max_cost
        if headers is not None:
            body["headers"] = headers
        if wait_for is not None:
            body["wait_for"] = wait_for
        if timeout is not None:
            body["timeout"] = timeout
        if js_scenario is not None:
            body["js_scenario"] = js_scenario

        response = await self._client.post("/v1/web/scrape", json=body)
        return ScrapeResult.model_validate(response)

    async def screenshot(
        self,
        url: str,
        *,
        full_page: bool = False,
        viewport_width: int = 1280,
        viewport_height: int = 720,
        image_format: str = "png",
        wait_for: str | None = None,
        timeout: float | None = None,
    ) -> ScreenshotResult:
        """Take a screenshot of a web page.

        Args:
            url: URL to screenshot.
            full_page: Capture full page (not just viewport).
            viewport_width: Viewport width in pixels.
            viewport_height: Viewport height in pixels.
            image_format: Image format (png, jpeg).
            wait_for: CSS selector to wait for.
            timeout: Request timeout in seconds.

        Returns:
            ScreenshotResult with base64 image data.
        """
        body: dict[str, Any] = {"url": url}
        if full_page:
            body["full_page"] = True
        if viewport_width != 1280:
            body["viewport_width"] = viewport_width
        if viewport_height != 720:
            body["viewport_height"] = viewport_height
        if image_format != "png":
            body["image_format"] = image_format
        if wait_for is not None:
            body["wait_for"] = wait_for
        if timeout is not None:
            body["timeout"] = timeout

        response = await self._client.post("/v1/web/screenshot", json=body)
        return ScreenshotResult.model_validate(response)

    async def extract(
        self,
        url: str,
        *,
        schema: dict[str, Any] | None = None,
        render_js: bool = False,
        wait_for: str | None = None,
        timeout: float | None = None,
    ) -> ExtractResult:
        """Extract structured data from a web page.

        Args:
            url: URL to extract from.
            schema: Extraction schema (CSS/XPath selectors).
            render_js: Whether to render JavaScript.
            wait_for: CSS selector to wait for.
            timeout: Request timeout in seconds.

        Returns:
            ExtractResult with extracted data.
        """
        body: dict[str, Any] = {"url": url}
        if schema is not None:
            body["extraction_schema"] = schema
        if render_js:
            body["render_js"] = True
        if wait_for is not None:
            body["wait_for"] = wait_for
        if timeout is not None:
            body["timeout"] = timeout

        response = await self._client.post("/v1/web/extract", json=body)
        return ExtractResult.model_validate(response)

    async def batch(
        self,
        urls: list[str],
        *,
        render_js: bool = False,
        output_format: str = "html",
        max_concurrency: int = 5,
        engine: str | None = None,
        timeout: float | None = None,
    ) -> BatchResult:
        """Scrape multiple URLs in a batch.

        Args:
            urls: List of URLs to scrape.
            render_js: Whether to render JavaScript.
            output_format: Output format (html, markdown, text, json).
            max_concurrency: Maximum concurrent requests.
            engine: Force a specific engine.
            timeout: Request timeout in seconds.

        Returns:
            BatchResult with results for each URL.
        """
        body: dict[str, Any] = {"urls": urls}
        if render_js:
            body["render_js"] = True
        if output_format != "html":
            body["output_format"] = output_format
        if max_concurrency != 5:
            body["max_concurrency"] = max_concurrency
        if engine is not None:
            body["engine"] = engine
        if timeout is not None:
            body["timeout"] = timeout

        response = await self._client.post("/v1/web/batch", json=body)
        return BatchResult.model_validate(response)

    async def create_session(
        self,
        domain: str,
        *,
        persist: bool = True,
    ) -> SessionInfo:
        """Create a new scraping session for a domain.

        Sessions maintain cookies, fingerprints, and state across requests.

        Args:
            domain: Domain to create session for.
            persist: Whether to persist session across requests.

        Returns:
            SessionInfo with session ID for reuse.
        """
        body: dict[str, Any] = {
            "domain": domain,
            "new_session": True,
            "persist_session": persist,
        }
        response = await self._client.post("/v1/web/sessions", json=body)
        return SessionInfo.model_validate(response)
