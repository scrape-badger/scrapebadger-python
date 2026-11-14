from unittest.mock import AsyncMock

import pytest

from scrapebadger.grok.client import GrokClient


@pytest.mark.asyncio
async def test_generated_grok_client_calls_all_public_operations():
    base = AsyncMock()
    base.get.return_value = {"answer": "Vilnius."}
    base.post.return_value = {"answer": "Vilnius."}
    client = GrokClient(base)

    await client.ask_grok_a_question(
        prompt="Capital?", conversation_id="42:123", mode="expert", web_search="off"
    )
    await client.ask_grok_a_question_post(payload={"prompt": "Capital?"})
    await client.measure_brand_visibility_in_grok(
        prompt="Best APIs", brand="ScrapeBadger", competitors=["Apify"]
    )
    await client.measure_brand_visibility_in_grok_post(payload={"prompt": "Best APIs"})
    await client.get_a_grok_conversation("42:123")
    await client.list_grok_assistant_modes()

    base.get.assert_any_await(
        "/v1/grok/ask",
        params={
            "prompt": "Capital?",
            "conversation_id": "42:123",
            "mode": "expert",
            "web_search": "off",
        },
    )
    base.get.assert_any_await(
        "/v1/grok/brand-visibility",
        params={
            "prompt": "Best APIs",
            "brand": "ScrapeBadger",
            "competitors": ["Apify"],
            "mode": "auto",
            "web_search": "force",
        },
    )
    base.get.assert_any_await("/v1/grok/conversations/42:123")
    base.get.assert_any_await("/v1/grok/models")
    assert base.post.await_count == 2
