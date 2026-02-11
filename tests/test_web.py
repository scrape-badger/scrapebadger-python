"""Unit tests for Python SDK web scraping methods."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock

import pytest

from scrapebadger.web.models import (
    BatchResult,
    ExtractResult,
    ScrapeResult,
    ScreenshotResult,
    SessionInfo,
)

if TYPE_CHECKING:
    from scrapebadger.web.client import WebClient

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class TestScrapeResult:
    def test_scrape_result(self) -> None:
        result = ScrapeResult(
            content="<html>hello</html>",
            status_code=200,
            url="https://example.com",
            engine_used="curl_cffi",
            credits_used=1,
        )
        assert result.content == "<html>hello</html>"
        assert result.status_code == 200
        assert result.engine_used == "curl_cffi"

    def test_screenshot_result(self) -> None:
        result = ScreenshotResult(
            image_data="base64data",
            format="png",
            url="https://example.com",
            credits_used=5,
        )
        assert result.image_data == "base64data"
        assert result.format == "png"

    def test_extract_result(self) -> None:
        result = ExtractResult(
            data={"title": "Hello", "price": "$10"},
            url="https://example.com",
            credits_used=2,
        )
        assert result.data["title"] == "Hello"

    def test_batch_result(self) -> None:
        result = BatchResult(
            results=[
                ScrapeResult(content="a", status_code=200, url="https://a.com"),
                ScrapeResult(content="b", status_code=200, url="https://b.com"),
            ],
            total=2,
            successful=2,
            failed=0,
        )
        assert result.total == 2
        assert len(result.results) == 2

    def test_session_info(self) -> None:
        info = SessionInfo(
            session_id="sess-123",
            domain="example.com",
            reused=False,
        )
        assert info.session_id == "sess-123"


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
            "content": "<html>test</html>",
            "status_code": 200,
            "url": "https://example.com",
            "engine_used": "curl_cffi",
            "credits_used": 1,
        }
        result = await web_client.scrape("https://example.com")
        assert isinstance(result, ScrapeResult)
        assert result.content == "<html>test</html>"
        mock_base_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_scrape_with_options(
        self, web_client: WebClient, mock_base_client: AsyncMock
    ) -> None:
        mock_base_client.post.return_value = {
            "content": "<html>test</html>",
            "status_code": 200,
            "url": "https://example.com",
            "engine_used": "patchright",
            "credits_used": 5,
        }
        result = await web_client.scrape(
            "https://example.com",
            render_js=True,
            proxy_country="US",
            output_format="markdown",
        )
        assert result.engine_used == "patchright"
        call_kwargs = mock_base_client.post.call_args
        body = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")
        assert body["render_js"] is True
        assert body["proxy_country"] == "US"

    @pytest.mark.asyncio
    async def test_screenshot(self, web_client: WebClient, mock_base_client: AsyncMock) -> None:
        mock_base_client.post.return_value = {
            "image_data": "base64png",
            "format": "png",
            "url": "https://example.com",
            "credits_used": 5,
        }
        result = await web_client.screenshot("https://example.com")
        assert isinstance(result, ScreenshotResult)
        assert result.image_data == "base64png"

    @pytest.mark.asyncio
    async def test_extract(self, web_client: WebClient, mock_base_client: AsyncMock) -> None:
        mock_base_client.post.return_value = {
            "data": {"title": "Test Page"},
            "url": "https://example.com",
            "credits_used": 3,
        }
        result = await web_client.extract(
            "https://example.com",
            schema={"title": "css:h1"},
        )
        assert isinstance(result, ExtractResult)
        assert result.data["title"] == "Test Page"

    @pytest.mark.asyncio
    async def test_batch(self, web_client: WebClient, mock_base_client: AsyncMock) -> None:
        mock_base_client.post.return_value = {
            "results": [
                {"content": "a", "status_code": 200, "url": "https://a.com"},
                {"content": "b", "status_code": 200, "url": "https://b.com"},
            ],
            "total": 2,
            "successful": 2,
            "failed": 0,
        }
        result = await web_client.batch(["https://a.com", "https://b.com"])
        assert isinstance(result, BatchResult)
        assert result.total == 2

    @pytest.mark.asyncio
    async def test_create_session(self, web_client: WebClient, mock_base_client: AsyncMock) -> None:
        mock_base_client.post.return_value = {
            "session_id": "sess-abc",
            "domain": "example.com",
            "reused": False,
        }
        result = await web_client.create_session("example.com")
        assert isinstance(result, SessionInfo)
        assert result.session_id == "sess-abc"

    @pytest.mark.asyncio
    async def test_scrape_with_session(
        self, web_client: WebClient, mock_base_client: AsyncMock
    ) -> None:
        mock_base_client.post.return_value = {
            "content": "<html>session</html>",
            "status_code": 200,
            "url": "https://example.com",
            "session_id": "sess-abc",
            "session_reused": True,
        }
        result = await web_client.scrape(
            "https://example.com",
            session_id="sess-abc",
        )
        assert result.content == "<html>session</html>"
        call_kwargs = mock_base_client.post.call_args
        body = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")
        assert body["session_id"] == "sess-abc"
