"""Unit tests for Python SDK web scraping methods."""

from __future__ import annotations

import base64
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock

import pytest

from scrapebadger.web.models import DetectResult, ExtractResult, ScrapeResult, ScreenshotResult

if TYPE_CHECKING:
    from scrapebadger.web.client import WebClient

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class TestScrapeResult:
    def test_scrape_result(self) -> None:
        result = ScrapeResult(
            success=True,
            content="<html>hello</html>",
            status_code=200,
            url="https://scrapebadger.com",
            engine_used="curl_cffi",
            credits_used=1,
            duration_ms=150,
        )
        assert result.content == "<html>hello</html>"
        assert result.status_code == 200
        assert result.engine_used == "curl_cffi"
        assert result.duration_ms == 150

    def test_scrape_result_with_ai_extraction(self) -> None:
        result = ScrapeResult(
            success=True,
            url="https://scrapebadger.com",
            status_code=200,
            ai_extraction={"title": "Hello", "price": "$10"},
            ai_model="gpt-4o-mini",
            credits_used=5,
        )
        assert result.ai_extraction == {"title": "Hello", "price": "$10"}
        assert result.ai_model == "gpt-4o-mini"

    def test_scrape_result_with_blocking(self) -> None:
        result = ScrapeResult(
            success=False,
            url="https://scrapebadger.com",
            status_code=403,
            blocking_detected=True,
            antibot_systems=[{"name": "cloudflare", "confidence": 0.95}],
        )
        assert result.blocking_detected is True
        assert len(result.antibot_systems) == 1

    def test_detect_result(self) -> None:
        result = DetectResult(
            url="https://scrapebadger.com",
            antibot_systems=[{"name": "cloudflare", "confidence": 0.95}],
            captcha_systems=[{"name": "recaptcha_v2"}],
            is_blocked=True,
            blocking_type="waf",
            recommendation="Use anti_bot=True",
            credits_used=1,
            duration_ms=200,
        )
        assert result.is_blocked is True
        assert result.blocking_type == "waf"
        assert len(result.antibot_systems) == 1
        assert len(result.captcha_systems) == 1


# ---------------------------------------------------------------------------
# WebClient methods
# ---------------------------------------------------------------------------


class TestWebClient:
    @pytest.fixture()
    def mock_base_client(self) -> AsyncMock:
        client = AsyncMock()
        return client

    @pytest.fixture()
    def web_client(self, mock_base_client: AsyncMock) -> WebClient:
        from scrapebadger.web.client import WebClient

        return WebClient(mock_base_client)

    @pytest.mark.asyncio
    async def test_scrape(self, web_client: WebClient, mock_base_client: AsyncMock) -> None:
        mock_base_client.post.return_value = {
            "success": True,
            "content": "<html>test</html>",
            "status_code": 200,
            "url": "https://scrapebadger.com",
            "engine_used": "curl_cffi",
            "credits_used": 1,
            "duration_ms": 120,
        }
        result = await web_client.scrape("https://scrapebadger.com")
        assert isinstance(result, ScrapeResult)
        assert result.content == "<html>test</html>"
        mock_base_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_scrape_with_options(
        self, web_client: WebClient, mock_base_client: AsyncMock
    ) -> None:
        mock_base_client.post.return_value = {
            "success": True,
            "content": "# Test",
            "status_code": 200,
            "url": "https://scrapebadger.com",
            "format": "markdown",
            "engine_used": "patchright",
            "credits_used": 5,
            "duration_ms": 500,
        }
        result = await web_client.scrape(
            "https://scrapebadger.com",
            render_js=True,
            country="US",
            format="markdown",
        )
        assert result.engine_used == "patchright"
        call_kwargs = mock_base_client.post.call_args
        body = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")
        assert body["render_js"] is True
        assert body["country"] == "US"
        assert body["format"] == "markdown"

    @pytest.mark.asyncio
    async def test_scrape_with_screenshot_and_video(
        self, web_client: WebClient, mock_base_client: AsyncMock
    ) -> None:
        mock_base_client.post.return_value = {
            "success": True,
            "url": "https://scrapebadger.com",
            "status_code": 200,
            "screenshot_url": "https://cdn.scrapebadger.com/screenshots/abc.png",
            "video_url": "https://cdn.scrapebadger.com/videos/abc.webm",
            "credits_used": 10,
            "duration_ms": 2000,
        }
        result = await web_client.scrape(
            "https://scrapebadger.com",
            screenshot=True,
            video=True,
        )
        assert result.screenshot_url is not None
        assert result.video_url is not None
        call_kwargs = mock_base_client.post.call_args
        body = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")
        assert body["screenshot"] is True
        assert body["video"] is True

    @pytest.mark.asyncio
    async def test_extract(self, web_client: WebClient, mock_base_client: AsyncMock) -> None:
        mock_base_client.post.return_value = {
            "success": True,
            "url": "https://scrapebadger.com",
            "status_code": 200,
            "ai_extraction": {"title": "Test Page", "description": "A test"},
            "ai_model": "gpt-4o-mini",
            "credits_used": 3,
            "duration_ms": 800,
        }
        result = await web_client.extract(
            "https://scrapebadger.com",
            prompt="Extract the title and description",
        )
        assert isinstance(result, ScrapeResult)
        assert result.ai_extraction == {"title": "Test Page", "description": "A test"}
        call_kwargs = mock_base_client.post.call_args
        body = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")
        assert body["ai_extract"] is True
        assert body["ai_prompt"] == "Extract the title and description"
        assert body["format"] == "markdown"

    @pytest.mark.asyncio
    async def test_detect(self, web_client: WebClient, mock_base_client: AsyncMock) -> None:
        mock_base_client.post.return_value = {
            "url": "https://scrapebadger.com",
            "antibot_systems": [{"name": "cloudflare", "confidence": 0.95}],
            "captcha_systems": [],
            "is_blocked": True,
            "blocking_type": "waf",
            "recommendation": "Use anti_bot=True with render_js=True",
            "credits_used": 1,
            "duration_ms": 300,
        }
        result = await web_client.detect("https://scrapebadger.com")
        assert isinstance(result, DetectResult)
        assert result.is_blocked is True
        assert len(result.antibot_systems) == 1
        mock_base_client.post.assert_called_once_with(
            "/v1/web/detect", json={"url": "https://scrapebadger.com"}
        )

    @pytest.mark.asyncio
    async def test_detect_with_options(
        self, web_client: WebClient, mock_base_client: AsyncMock
    ) -> None:
        mock_base_client.post.return_value = {
            "url": "https://scrapebadger.com",
            "antibot_systems": [],
            "captcha_systems": [],
            "is_blocked": False,
            "credits_used": 1,
            "duration_ms": 200,
        }
        await web_client.detect(
            "https://scrapebadger.com",
            timeout=5000,
            country="US",
        )
        call_kwargs = mock_base_client.post.call_args
        body = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")
        assert body["timeout"] == 5000
        assert body["country"] == "US"

    @pytest.mark.asyncio
    async def test_scrape_with_session(
        self, web_client: WebClient, mock_base_client: AsyncMock
    ) -> None:
        mock_base_client.post.return_value = {
            "success": True,
            "content": "<html>session</html>",
            "status_code": 200,
            "url": "https://scrapebadger.com",
            "credits_used": 1,
            "duration_ms": 100,
        }
        result = await web_client.scrape(
            "https://scrapebadger.com",
            session_id="sess-abc",
        )
        assert result.content == "<html>session</html>"
        call_kwargs = mock_base_client.post.call_args
        body = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")
        assert body["session_id"] == "sess-abc"

    @pytest.mark.asyncio
    async def test_scrape_screenshot_full_page_and_window(
        self, web_client: WebClient, mock_base_client: AsyncMock
    ) -> None:
        mock_base_client.post.return_value = {"success": True, "url": "https://x.com"}
        await web_client.scrape(
            "https://x.com",
            screenshot=True,
            screenshot_full_page=True,
            window_width=1280,
            window_height=720,
        )
        body = mock_base_client.post.call_args.kwargs["json"]
        assert body["screenshot"] is True
        assert body["screenshot_full_page"] is True
        assert body["window_width"] == 1280
        assert body["window_height"] == 720

    @pytest.mark.asyncio
    async def test_scrape_omits_unset_window_options(
        self, web_client: WebClient, mock_base_client: AsyncMock
    ) -> None:
        mock_base_client.post.return_value = {"success": True}
        await web_client.scrape("https://x.com")
        mock_base_client.post.assert_called_once_with(
            "/v1/web/scrape", json={"url": "https://x.com"}
        )


PNG = b"\x89PNG\r\n\x1a\n" + bytes(range(16))


class TestScreenshot:
    @pytest.fixture()
    def mock_base_client(self) -> AsyncMock:
        client = AsyncMock()
        client.post.return_value = {
            "success": True,
            "url": "https://www.example.com/",
            "status_code": 200,
            "content_type": "image/png",
            "screenshot": base64.b64encode(PNG).decode(),
            "engine_used": "cloakbrowser",
            "credits_used": 6,
            "duration_ms": 4210,
        }
        return client

    @pytest.fixture()
    def web_client(self, mock_base_client: AsyncMock) -> WebClient:
        from scrapebadger.web.client import WebClient as _WebClient

        return _WebClient(mock_base_client)

    async def test_defaults_send_only_the_url(
        self, web_client: WebClient, mock_base_client: AsyncMock
    ) -> None:
        result = await web_client.screenshot("https://example.com")

        assert isinstance(result, ScreenshotResult)
        assert result.credits_used == 6
        mock_base_client.post.assert_called_once_with(
            "/v1/web/screenshot", json={"url": "https://example.com"}
        )

    async def test_options_map_to_the_request_body(
        self, web_client: WebClient, mock_base_client: AsyncMock
    ) -> None:
        await web_client.screenshot(
            "https://example.com",
            full_page=True,
            width=1280,
            height=800,
            wait_for="#main",
            country="DE",
            proxy_tier="premium",
        )

        assert mock_base_client.post.call_args.kwargs["json"] == {
            "url": "https://example.com",
            "full_page": True,
            "width": 1280,
            "height": 800,
            "wait_for": "#main",
            "country": "DE",
            "proxy_tier": "premium",
        }

    async def test_png_decodes_and_save_writes_the_file(
        self, web_client: WebClient, tmp_path
    ) -> None:
        result = await web_client.screenshot("https://example.com")

        assert result.png == PNG
        saved = result.save(tmp_path / "page.png")
        assert saved.read_bytes() == PNG


class TestExtractData:
    @pytest.fixture()
    def mock_base_client(self) -> AsyncMock:
        client = AsyncMock()
        client.post.return_value = {
            "success": True,
            "url": "https://news.ycombinator.com/",
            "status_code": 200,
            "data": {"top_story": "Hello", "links": ["https://a", "https://b"]},
            "ai_extraction": None,
            "ai_model": None,
            "ai_error": None,
            "engine_used": "http",
            "credits_used": 2,
            "duration_ms": 1384,
        }
        return client

    @pytest.fixture()
    def web_client(self, mock_base_client: AsyncMock) -> WebClient:
        from scrapebadger.web.client import WebClient as _WebClient

        return _WebClient(mock_base_client)

    async def test_selector_rules_go_to_the_extract_endpoint(
        self, web_client: WebClient, mock_base_client: AsyncMock
    ) -> None:
        rules = {
            "top_story": ".titleline a",
            "links": {"selector": ".titleline a::attr(href)", "all": True},
        }
        result = await web_client.extract_data("https://news.ycombinator.com", extract_rules=rules)

        assert isinstance(result, ExtractResult)
        assert result.data == {"top_story": "Hello", "links": ["https://a", "https://b"]}
        assert result.ai_extraction is None
        mock_base_client.post.assert_called_once_with(
            "/v1/web/extract",
            json={"url": "https://news.ycombinator.com", "extract_rules": rules},
        )

    async def test_ai_options_map_to_the_request_body(
        self, web_client: WebClient, mock_base_client: AsyncMock
    ) -> None:
        await web_client.extract_data(
            "https://example.com",
            ai_extract_rules={"price": "the product price"},
            ai_query="Is it in stock?",
            render_js=True,
            wait_for=".price",
            country="US",
            proxy_tier="ultra",
        )

        assert mock_base_client.post.call_args.kwargs["json"] == {
            "url": "https://example.com",
            "ai_extract_rules": {"price": "the product price"},
            "ai_query": "Is it in stock?",
            "render_js": True,
            "wait_for": ".price",
            "country": "US",
            "proxy_tier": "ultra",
        }

    async def test_nothing_to_extract_raises_before_any_request(
        self, web_client: WebClient, mock_base_client: AsyncMock
    ) -> None:
        with pytest.raises(ValueError, match="at least one of"):
            await web_client.extract_data("https://example.com")
        mock_base_client.post.assert_not_called()


class TestBatchDeprecated:
    """Batch was never built: the API answers 501. The methods stay, but warn."""

    async def test_submit_and_status_warn(self) -> None:
        from scrapebadger.web.client import WebClient as _WebClient

        base = AsyncMock()
        web = _WebClient(base)

        with pytest.warns(DeprecationWarning, match="concurrent"):
            await web.submit_batch_scraping_job(payload={"urls": ["https://x.com"]})
        with pytest.warns(DeprecationWarning, match="concurrent"):
            await web.get_batch_job_status("job-1")
        base.get.assert_called_once_with("/v1/web/batch/job-1")


class TestRawContent:
    """`raw_content=True` returns a non-JSON body.

    The transport's `response.json()` fell back to `{}` on a parse failure, so
    every raw scrape silently produced an empty ScrapeResult and no error. These
    pin the raw path, including that binary payloads are never decoded.
    """

    @pytest.fixture()
    def mock_base_client(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture()
    def web_client(self, mock_base_client: AsyncMock) -> WebClient:
        from scrapebadger.web.client import WebClient as _WebClient

        return _WebClient(mock_base_client)

    async def test_binary_body_is_returned_undecoded(
        self, web_client: WebClient, mock_base_client: AsyncMock
    ) -> None:
        png = b"\x89PNG\r\n\x1a\n" + bytes(range(256))
        mock_base_client.post_raw.return_value = (
            png,
            {
                "Content-Type": "image/png",
                "X-Scrape-Status-Code": "200",
                "X-Credits-Used": "2",
                "X-Scrape-Engine": "httpcloak",
            },
            200,
        )

        result = await web_client.scrape("https://x.com/a.png", raw_content=True)

        assert result.content_bytes == png, "bytes must survive untouched"
        assert result.content is None, "decoding an image is the bug we are fixing"
        assert result.is_binary is True
        assert result.content_type == "image/png"
        assert result.credits_used == 2
        assert result.engine_used == "httpcloak"
        # The JSON path must not have been used at all.
        mock_base_client.post.assert_not_called()

    async def test_text_body_is_decoded(
        self, web_client: WebClient, mock_base_client: AsyncMock
    ) -> None:
        mock_base_client.post_raw.return_value = (
            b"<html>hi</html>",
            {"Content-Type": "text/html; charset=utf-8", "X-Scrape-Status-Code": "200"},
            200,
        )

        result = await web_client.scrape("https://x.com", raw_content=True)

        assert result.content == "<html>hi</html>"
        assert result.content_bytes == b"<html>hi</html>"
        assert result.is_binary is False

    async def test_without_raw_content_the_json_path_is_used(
        self, web_client: WebClient, mock_base_client: AsyncMock
    ) -> None:
        mock_base_client.post.return_value = {"success": True, "content": "<html/>"}

        result = await web_client.scrape("https://x.com")

        assert result.content == "<html/>"
        mock_base_client.post_raw.assert_not_called()
