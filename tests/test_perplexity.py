"""Unit tests for the Perplexity SDK client — query building for strict_country."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from scrapebadger.perplexity.client import PerplexityClient


@pytest.fixture
def base() -> MagicMock:
    client = MagicMock()
    client.get = AsyncMock(return_value={})
    return client


@pytest.fixture
def perplexity(base: MagicMock) -> PerplexityClient:
    return PerplexityClient(base)


async def test_ask_omits_strict_country_by_default(
    perplexity: PerplexityClient, base: MagicMock
) -> None:
    await perplexity.ask_perplexity_a_question(prompt="q", country="DE")
    base.get.assert_awaited_once_with("/v1/perplexity/ask", params={"prompt": "q", "country": "DE"})


async def test_ask_sends_strict_country_when_true(
    perplexity: PerplexityClient, base: MagicMock
) -> None:
    await perplexity.ask_perplexity_a_question(prompt="q", country="DE", strict_country=True)
    base.get.assert_awaited_once_with(
        "/v1/perplexity/ask", params={"prompt": "q", "country": "DE", "strict_country": True}
    )


async def test_brand_visibility_strict_country(
    perplexity: PerplexityClient, base: MagicMock
) -> None:
    await perplexity.measure_a_brand_s_visibility_in_a_perplexity_answer(
        prompt="q", brand="Nike", country="JP", strict_country=True
    )
    base.get.assert_awaited_once_with(
        "/v1/perplexity/brand-visibility",
        params={"prompt": "q", "brand": "Nike", "country": "JP", "strict_country": True},
    )
    base.get.reset_mock()
    await perplexity.measure_a_brand_s_visibility_in_a_perplexity_answer(prompt="q", brand="Nike")
    assert "strict_country" not in base.get.await_args.kwargs["params"]
