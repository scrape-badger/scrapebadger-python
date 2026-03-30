"""Unit tests for Python SDK web scraping methods."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock

import pytest

from scrapebadger.web.models import DetectResult, ScrapeResult

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
