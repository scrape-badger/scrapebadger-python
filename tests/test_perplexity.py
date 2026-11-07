"""Unit tests for the Perplexity SDK client — query building for strict_country and location."""

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


async def test_ask_sends_false_strict_country_default(
    perplexity: PerplexityClient, base: MagicMock
) -> None:
    await perplexity.ask_perplexity_a_question(prompt="q", country="DE")
    base.get.assert_awaited_once_with(
        "/v1/perplexity/ask", params={"prompt": "q", "country": "DE", "strict_country": False}
    )


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
    assert base.get.await_args.kwargs["params"]["strict_country"] is False


async def test_ask_omits_location_by_default(perplexity: PerplexityClient, base: MagicMock) -> None:
    await perplexity.ask_perplexity_a_question(prompt="q", country="JP")
    assert "location" not in base.get.await_args.kwargs["params"]


async def test_ask_sends_location(perplexity: PerplexityClient, base: MagicMock) -> None:
    await perplexity.ask_perplexity_a_question(
        prompt="best dentist", country="JP", strict_country=True, location="tokyo"
    )
    base.get.assert_awaited_once_with(
        "/v1/perplexity/ask",
        params={
            "prompt": "best dentist",
            "country": "JP",
            "strict_country": True,
            "location": "tokyo",
        },
    )


async def test_location_is_sent_as_given(perplexity: PerplexityClient, base: MagicMock) -> None:
    # The server folds and validates; the SDK must not rewrite or reject.
    await perplexity.ask_perplexity_a_question(prompt="q", location="New York")
    assert base.get.await_args.kwargs["params"]["location"] == "New York"
    base.get.reset_mock()
    await perplexity.ask_perplexity_a_question(prompt="q", location="35.6812,139.7671")
    assert base.get.await_args.kwargs["params"]["location"] == "35.6812,139.7671"


async def test_brand_visibility_location(perplexity: PerplexityClient, base: MagicMock) -> None:
    await perplexity.measure_a_brand_s_visibility_in_a_perplexity_answer(
        prompt="q", brand="Nike", country="JP", location="osaka"
    )
    base.get.assert_awaited_once_with(
        "/v1/perplexity/brand-visibility",
        params={
            "prompt": "q",
            "brand": "Nike",
            "country": "JP",
            "strict_country": False,
            "location": "osaka",
        },
    )
    base.get.reset_mock()
    await perplexity.measure_a_brand_s_visibility_in_a_perplexity_answer(prompt="q", brand="Nike")
    assert "location" not in base.get.await_args.kwargs["params"]
