"""Skipping the duplicate-request cache: ``no_cache`` and ``with_options``."""

from __future__ import annotations

import httpx
import respx

from scrapebadger import ScrapeBadger
from scrapebadger._internal.config import ClientConfig

BASE = "https://api.test.scrapebadger.com"
ASK = f"{BASE}/v1/perplexity/ask"
ANSWER = {"answer": "ok", "sources": []}


def _cache_control(route: respx.Route, call: int = -1) -> str | None:
    return route.calls[call].request.headers.get("cache-control")


def test_config_defaults_to_cached() -> None:
    config = ClientConfig(api_key="k")
    assert config.no_cache is False
    assert config.with_overrides(timeout=5.0).no_cache is False
    assert config.with_overrides(no_cache=True).no_cache is True


def test_client_kwarg_sets_config() -> None:
    assert ScrapeBadger(api_key="k").config.no_cache is False
    assert ScrapeBadger(api_key="k", no_cache=True).config.no_cache is True


@respx.mock
async def test_header_absent_by_default(client: ScrapeBadger) -> None:
    route = respx.get(ASK).mock(return_value=httpx.Response(200, json=ANSWER))
    await client.perplexity.ask_perplexity_a_question(prompt="q")
    assert _cache_control(route) is None


@respx.mock
async def test_client_level_no_cache_sends_header() -> None:
    route = respx.get(ASK).mock(return_value=httpx.Response(200, json=ANSWER))
    async with ScrapeBadger(api_key="k", base_url=BASE, no_cache=True) as client:
        await client.perplexity.ask_perplexity_a_question(prompt="q")
    assert _cache_control(route) == "no-cache"


@respx.mock
async def test_with_options_post_and_get_leave_parent_cached(client: ScrapeBadger) -> None:
    post = respx.post(ASK).mock(return_value=httpx.Response(200, json=ANSWER))
    get = respx.get(f"{BASE}/v1/twitter/users/jack/by_username").mock(
        return_value=httpx.Response(200, json={"id": "12", "username": "jack", "name": "jack"})
    )
    fresh = client.with_options(no_cache=True)

    await fresh.perplexity.ask_perplexity_a_question_post(payload={"prompt": "q"})
    await fresh.twitter.users.get_by_username("jack")
    await client.perplexity.ask_perplexity_a_question_post(payload={"prompt": "q"})
    await client.twitter.users.get_by_username("jack")

    assert _cache_control(post, 0) == "no-cache"
    assert _cache_control(get, 0) == "no-cache"
    assert _cache_control(post, 1) is None
    assert _cache_control(get, 1) is None
    # The API key still goes with every request, borrowed pool or not.
    assert all(c.request.headers["x-api-key"] == "test_api_key_12345" for c in respx.calls)
    assert client.config.no_cache is False
    assert fresh.config.no_cache is True


@respx.mock
async def test_with_options_can_turn_no_cache_off() -> None:
    route = respx.get(ASK).mock(return_value=httpx.Response(200, json=ANSWER))
    async with ScrapeBadger(api_key="k", base_url=BASE, no_cache=True) as client:
        await client.with_options(no_cache=False).perplexity.ask_perplexity_a_question(prompt="q")
    assert _cache_control(route) is None


@respx.mock
async def test_post_raw_sends_header(client: ScrapeBadger) -> None:
    route = respx.post(f"{BASE}/v1/web/scrape").mock(
        return_value=httpx.Response(200, content=b"<html></html>")
    )
    base = client.with_options(no_cache=True)._base_client
    await base.post_raw("/v1/web/scrape", json={"url": "https://example.com"})
    assert _cache_control(route) == "no-cache"


@respx.mock
async def test_get_raw_sends_header(client: ScrapeBadger) -> None:
    route = respx.get(f"{BASE}/v1/google/search").mock(
        return_value=httpx.Response(200, content=b"<html></html>")
    )
    await client.with_options(no_cache=True)._base_client.get_raw("/v1/google/search")
    assert _cache_control(route) == "no-cache"


@respx.mock
async def test_with_options_merges_headers_and_sends_timeout() -> None:
    route = respx.get(ASK).mock(return_value=httpx.Response(200, json=ANSWER))
    config = ClientConfig(api_key="k", base_url=BASE, headers={"X-Parent": "1"})
    async with ScrapeBadger(config=config) as client:
        child = client.with_options(headers={"X-Child": "2"}, timeout=12.0)
        await child.perplexity.ask_perplexity_a_question(prompt="q")
        assert client.config.headers == {"X-Parent": "1"}
    request = route.calls.last.request
    assert request.headers["x-parent"] == "1"
    assert request.headers["x-child"] == "2"
    assert request.extensions["timeout"]["read"] == 12.0


async def test_clone_shares_pool_and_closing_it_keeps_parent_open() -> None:
    async with ScrapeBadger(api_key="k", base_url=BASE) as client:
        parent_pool = await client._base_client._get_client()
        clone = client.with_options(no_cache=True)
        async with clone:
            assert await clone._base_client._get_client() is parent_pool
        assert not parent_pool.is_closed
    assert parent_pool.is_closed


async def test_clone_with_other_base_url_owns_its_pool() -> None:
    async with ScrapeBadger(api_key="k", base_url=BASE) as client:
        parent_pool = await client._base_client._get_client()
        other = client.with_options(base_url="https://other.test")
        other_pool = await other._base_client._get_client()
        assert other_pool is not parent_pool
        await other.close()
        assert other_pool.is_closed
        assert not parent_pool.is_closed


def test_with_options_builds_fresh_sub_clients() -> None:
    client = ScrapeBadger(api_key="k")
    parent_perplexity = client.perplexity
    clone = client.with_options(no_cache=True)
    assert clone.perplexity is not parent_perplexity
    assert client.perplexity is parent_perplexity
