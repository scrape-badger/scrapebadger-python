"""Unit tests for the ChatGPT SDK client — endpoint routing and full field coverage.

The SDK drops any field the model does not declare, so the parsing tests assert
every field in the API contract survives ``model_validate``.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from scrapebadger.chatgpt.client import ChatGPTClient
from scrapebadger.chatgpt.models import (
    AskResponse,
    BrandVisibilityResponse,
    ModelsResponse,
)

CITATION: dict[str, Any] = {
    "url": "https://reuters.com/a",
    "title": "A headline",
    "snippet": "A snippet",
    "domain": "reuters.com",
    "attribution": "Reuters",
    "pub_date_utc": 1754300000.0,
    "published_at": "2026-08-04T10:00:00Z",
    "start_index": 12,
    "end_index": 48,
    "matched_text": "the supported span",
}
SEARCH_RESULT: dict[str, Any] = {
    "url": "https://example.com/b",
    "title": "Another page",
    "snippet": "Another snippet",
    "domain": "example.com",
    "attribution": "Example",
    "pub_date_utc": 1754200000.0,
    "published_at": "2026-08-03T10:00:00Z",
    "ref_index": 3,
    "cited": False,
}
ASK_RESPONSE: dict[str, Any] = {
    "prompt": "best running shoes 2026",
    "answer": "Plain text answer.",
    "answer_markdown": "**Markdown** answer.",
    "citations": [CITATION],
    "search_results": [SEARCH_RESULT],
    "source_domains": ["reuters.com", "example.com"],
    "web_search_triggered": True,
    "reference_tokens": ["turn0search1", "turn0news20"],
    "model": "gpt-5-5",
    "conversation_id": "conv-1",
    "message_id": "msg-1",
    "country": "US",
    "answer_length": 18,
    "citation_count": 1,
    "latency_ms": 24310,
    "created_utc": 1754400000.0,
    "created_at": "2026-08-05T10:00:00Z",
}
BRAND_RESPONSE: dict[str, Any] = {
    "prompt": "best web scraping API",
    "brand": "ScrapeBadger",
    "domain": "scrapebadger.com",
    "mentioned": True,
    "mention_count": 3,
    "first_position": 42,
    "position_score": 0.83,
    "share_of_voice_pct": 37.5,
    "cited": True,
    "cited_urls": ["https://scrapebadger.com/"],
    "citation_rank": 2,
    "competitors": [
        {
            "name": "Bright Data",
            "mentioned": True,
            "mention_count": 5,
            "first_position": 10,
            "cited": True,
            "cited_urls": ["https://brightdata.com/"],
        }
    ],
    "excerpt": "...ScrapeBadger is a...",
    "answer": "Plain text answer.",
    "citations": [CITATION],
    "web_search_triggered": True,
    "model": "gpt-5-5",
    "country": "US",
    "latency_ms": 27100,
    "created_utc": 1754400000.0,
    "created_at": "2026-08-05T10:00:00Z",
}
MODELS_RESPONSE: dict[str, Any] = {
    "models": [
        {
            "slug": "gpt-5-5",
            "title": "GPT-5.5",
            "description": "Great for most questions",
            "max_tokens": 128000,
            "tags": ["default"],
        }
    ],
    "count": 1,
}


@pytest.fixture
def mock_base_client() -> MagicMock:
    client = MagicMock()
    client.get = AsyncMock()
    return client


@pytest.fixture
def chatgpt(mock_base_client: MagicMock) -> ChatGPTClient:
    return ChatGPTClient(mock_base_client)


# =============================================================================
# Routing
# =============================================================================


@pytest.mark.asyncio
async def test_ask_routes_and_defaults(chatgpt: ChatGPTClient, mock_base_client: MagicMock) -> None:
    mock_base_client.get.return_value = ASK_RESPONSE

    await chatgpt.ask.ask("best running shoes 2026")

    mock_base_client.get.assert_awaited_once_with(
        "/v1/chatgpt/ask",
        params={
            "prompt": "best running shoes 2026",
            "country": "US",
            "web_search": "auto",
        },
    )


@pytest.mark.asyncio
async def test_brand_visibility_joins_lists(
    chatgpt: ChatGPTClient, mock_base_client: MagicMock
) -> None:
    mock_base_client.get.return_value = BRAND_RESPONSE

    await chatgpt.brand.visibility(
        "best web scraping API",
        brand="ScrapeBadger",
        domain="scrapebadger.com",
        aliases=["Scrape Badger"],
        competitors=["Bright Data", "Apify"],
        country="DE",
    )

    mock_base_client.get.assert_awaited_once_with(
        "/v1/chatgpt/brand-visibility",
        params={
            "prompt": "best web scraping API",
            "brand": "ScrapeBadger",
            "domain": "scrapebadger.com",
            "aliases": "Scrape Badger",
            "competitors": "Bright Data,Apify",
            "country": "DE",
            "web_search": "force",
        },
    )


@pytest.mark.asyncio
async def test_brand_visibility_omits_empty_lists(
    chatgpt: ChatGPTClient, mock_base_client: MagicMock
) -> None:
    mock_base_client.get.return_value = BRAND_RESPONSE

    await chatgpt.brand.visibility("q", brand="ScrapeBadger")

    params = mock_base_client.get.await_args.kwargs["params"]
    assert params["aliases"] is None
    assert params["competitors"] is None
    assert params["domain"] is None


@pytest.mark.asyncio
async def test_models_routes(chatgpt: ChatGPTClient, mock_base_client: MagicMock) -> None:
    mock_base_client.get.return_value = MODELS_RESPONSE

    result = await chatgpt.reference.models(country="GB")

    mock_base_client.get.assert_awaited_once_with("/v1/chatgpt/models", params={"country": "GB"})
    assert isinstance(result, ModelsResponse)
    assert result.count == 1
    assert result.models[0].slug == "gpt-5-5"
    assert result.models[0].max_tokens == 128000
    assert result.models[0].tags == ["default"]


# =============================================================================
# Field coverage — nothing in the contract may be silently dropped
# =============================================================================


def test_ask_response_keeps_every_field() -> None:
    parsed = AskResponse.model_validate(ASK_RESPONSE)

    dumped = parsed.model_dump()
    for key, value in ASK_RESPONSE.items():
        if key in ("citations", "search_results"):
            continue
        assert dumped[key] == value, f"AskResponse dropped or changed {key}"

    citation = parsed.citations[0]
    assert citation.model_dump() == CITATION
    assert parsed.search_results[0].model_dump() == SEARCH_RESULT


def test_brand_response_keeps_every_field() -> None:
    parsed = BrandVisibilityResponse.model_validate(BRAND_RESPONSE)

    dumped = parsed.model_dump()
    for key, value in BRAND_RESPONSE.items():
        if key in ("citations", "competitors"):
            continue
        assert dumped[key] == value, f"BrandVisibilityResponse dropped or changed {key}"

    assert parsed.competitors[0].model_dump() == BRAND_RESPONSE["competitors"][0]
    assert parsed.citations[0].model_dump() == CITATION


def test_citation_offsets_index_the_untouched_answer() -> None:
    """Whitespace must not be stripped: it would shift every citation offset."""
    answer = "  padded answer  "
    parsed = AskResponse.model_validate({**ASK_RESPONSE, "answer": answer})
    assert parsed.answer == answer


@pytest.mark.asyncio
async def test_ask_omits_image_url_when_not_given(
    chatgpt: ChatGPTClient, mock_base_client: MagicMock
) -> None:
    """An existing call must be byte-identical on the wire."""
    mock_base_client.get.return_value = ASK_RESPONSE

    await chatgpt.ask.ask("best running shoes 2026")

    _, kwargs = mock_base_client.get.await_args
    assert "image_url" not in kwargs["params"]


@pytest.mark.asyncio
async def test_ask_sends_image_url_when_given(
    chatgpt: ChatGPTClient, mock_base_client: MagicMock
) -> None:
    mock_base_client.get.return_value = ASK_RESPONSE

    await chatgpt.ask.ask("what is in this photo?", image_url="https://example.com/a.png")

    _, kwargs = mock_base_client.get.await_args
    assert kwargs["params"]["image_url"] == "https://example.com/a.png"


def test_ask_response_parses_images() -> None:
    """`images` is what the answer DISPLAYED — ChatGPT never generates one."""
    parsed = AskResponse.model_validate(
        {**ASK_RESPONSE, "images": [{"url": "https://cdn.example/a.jpg", "title": "a shoe"}]}
    )
    assert [i.url for i in parsed.images] == ["https://cdn.example/a.jpg"]
    assert parsed.images[0].title == "a shoe"
    # Absent on an older payload, and that is not an error.
    assert AskResponse.model_validate(ASK_RESPONSE).images == []
