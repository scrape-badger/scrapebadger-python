"""Public SDK targeting and raw HTML transport."""

import httpx
import pytest
import respx

from scrapebadger import ScrapeBadger


@pytest.mark.parametrize("method,path", [("search", "search"), ("light", "light/search")])
@respx.mock
async def test_search_targeting_roundtrip(method, path):
    route = respx.get("https://example.test/v1/google/" + path).mock(
        return_value=httpx.Response(200, json={"organic_results": []})
    )
    async with ScrapeBadger(api_key="test", base_url="https://example.test") as client:
        result = await getattr(client.google.search, method)(
            "vinted api",
            location="New York, USA",
            no_cache=True,
            as_epq="vinted api",
            color_scheme="dark",
        )
    assert result == {"organic_results": []}
    sent = route.calls.last.request.url.params
    assert sent["location"] == "New York, USA"
    assert sent["no_cache"] == "true"
    assert sent["as_epq"] == "vinted api"
    assert sent["color_scheme"] == "dark"


@pytest.mark.parametrize("method,path", [("search", "search"), ("light", "light/search")])
@respx.mock
async def test_search_raw_html_is_not_lost(method, path):
    respx.get("https://example.test/v1/google/" + path).mock(
        return_value=httpx.Response(
            200, text="<html>café</html>", headers={"content-type": "text/html; charset=utf-8"}
        )
    )
    async with ScrapeBadger(api_key="test", base_url="https://example.test") as client:
        result = await getattr(client.google.search, method)("cafe", output="html")
    assert result == "<html>café</html>"
