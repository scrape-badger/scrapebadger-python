"""Unit tests for the Copilot SDK client — query building."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from scrapebadger import ScrapeBadger
from scrapebadger.copilot.client import CopilotClient


@pytest.fixture
def base() -> MagicMock:
    client = MagicMock()
    client.get = AsyncMock(return_value={})
    client.post = AsyncMock(return_value={})
    return client


@pytest.fixture
def copilot(base: MagicMock) -> CopilotClient:
    return CopilotClient(base)


def test_registered_on_client() -> None:
    assert isinstance(ScrapeBadger(api_key="k").copilot, CopilotClient)


async def test_ask_omits_unset_params(copilot: CopilotClient, base: MagicMock) -> None:
    await copilot.ask_copilot_a_question(prompt="q")
    base.get.assert_awaited_once_with("/v1/copilot/ask", params={"prompt": "q"})


async def test_ask_sends_market_and_strict_country(copilot: CopilotClient, base: MagicMock) -> None:
    await copilot.ask_copilot_a_question(
        prompt="q", country="JP", market="ja-JP", strict_country=True
    )
    base.get.assert_awaited_once_with(
        "/v1/copilot/ask",
        params={"prompt": "q", "country": "JP", "market": "ja-JP", "strict_country": True},
    )


async def test_brand_visibility_strict_country(copilot: CopilotClient, base: MagicMock) -> None:
    await copilot.measure_a_brand_s_visibility_in_a_copilot_answer(
        prompt="q", brand="freee", country="JP", strict_country=True
    )
    base.get.assert_awaited_once_with(
        "/v1/copilot/brand-visibility",
        params={"prompt": "q", "brand": "freee", "country": "JP", "strict_country": True},
    )


async def test_list_markets(copilot: CopilotClient, base: MagicMock) -> None:
    await copilot.list_copilot_markets()
    base.get.assert_awaited_once_with("/v1/copilot/markets")


async def test_post_forms(copilot: CopilotClient, base: MagicMock) -> None:
    body = {"prompt": "q", "country": "JP", "strict_country": True}
    await copilot.ask_copilot_a_question_post(payload=body)
    await copilot.measure_a_brand_s_visibility_in_a_copilot_answer_post(
        payload={**body, "brand": "freee"}
    )
    assert [c.args[0] for c in base.post.await_args_list] == [
        "/v1/copilot/ask",
        "/v1/copilot/brand-visibility",
    ]
    assert base.post.await_args_list[0].kwargs == {"params": None, "json": body}
