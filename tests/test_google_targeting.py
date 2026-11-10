"""Public SDK targeting and raw HTML transport."""

import httpx
import pytest
import respx

from scrapebadger import ScrapeBadger, ValidationError


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
            oq="vinted café + api&gl=fr",
            sourceid="",
            ie="UTF-8",
        )
    assert result == {"organic_results": []}
    sent = route.calls.last.request.url.params
    assert sent["location"] == "New York, USA"
    assert sent["no_cache"] == "true"
    assert sent["as_epq"] == "vinted api"
    assert sent["color_scheme"] == "dark"
    assert sent["oq"] == "vinted café + api&gl=fr"
    assert sent["sourceid"] == ""
    assert sent["ie"] == "UTF-8"


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


@pytest.mark.parametrize("body", [{"detail": "Conflicting targeting"}, "invalid targeting"])
@respx.mock
async def test_raw_html_still_raises_api_errors(body):
    response = (
        httpx.Response(422, json=body) if isinstance(body, dict) else httpx.Response(422, text=body)
    )
    respx.get("https://example.test/v1/google/search").mock(return_value=response)
    async with ScrapeBadger(api_key="test", base_url="https://example.test") as client:
        with pytest.raises(ValidationError):
            await client.google.search.search("cafe", output="html", location="invalid")


AI_MODE = "https://example.test/v1/google/ai-mode/search"


async def _ai_mode_params(**kwargs):
    """Send one AI Mode request and return the query string it carried."""
    with respx.mock:
        route = respx.get(AI_MODE).mock(
            return_value=httpx.Response(200, json={"text_blocks": [], "references": []})
        )
        async with ScrapeBadger(api_key="test", base_url="https://example.test") as client:
            await client.google.ai_mode.search("best coffee near me", **kwargs)
    return dict(route.calls.last.request.url.params)


async def test_ai_mode_unlocated_request_is_unchanged():
    assert await _ai_mode_params() == {
        "q": "best coffee near me",
        "gl": "us",
        "hl": "en",
        "include_html": "true",
    }


async def test_ai_mode_location_leaves_gl_to_the_location_country():
    sent = await _ai_mode_params(location="Wonju-si,Gangwon-do,South Korea", hl="ko")
    assert sent == {
        "q": "best coffee near me",
        "hl": "ko",
        "include_html": "true",
        "location": "Wonju-si,Gangwon-do,South Korea",
    }


async def test_ai_mode_location_keeps_an_explicit_gl():
    sent = await _ai_mode_params(location="1009889", gl="kr")
    assert (sent["location"], sent["gl"]) == ("1009889", "kr")


async def test_ai_mode_coordinates_and_uule():
    sent = await _ai_mode_params(lat=35.1763, lon=129.0798, include_html=False)
    assert (sent["lat"], sent["lon"], sent["gl"]) == ("35.1763", "129.0798", "us")
    assert sent["include_html"] == "false"
    assert "location" not in sent and "uule" not in sent

    wonju = "w+CAIQICIfV29uanUtc2ksR2FuZ3dvbi1kbyxTb3V0aCBLb3JlYQ"
    sent = await _ai_mode_params(uule=wonju, gl="kr")
    assert (sent["uule"], sent["gl"]) == (wonju, "kr")
    assert "lat" not in sent and "lon" not in sent


@respx.mock
async def test_ai_mode_returns_the_location_echo():
    echo = {
        "requested": "Jeju-si",
        "resolved": "Jeju-si,Jeju-do,South Korea",
        "latitude": None,
        "longitude": None,
        "uule": "w+CAIQICIbSmVqdS1zaSxKZWp1LWRvLFNvdXRoIEtvcmVh",
    }
    body = {"text_blocks": [], "country": "kr", "location": echo}
    respx.get(AI_MODE).mock(return_value=httpx.Response(200, json=body))
    async with ScrapeBadger(api_key="test", base_url="https://example.test") as client:
        answer = await client.google.ai_mode.search("weather", location="Jeju-si")
    assert answer["location"] == echo
    assert answer["country"] == "kr"


@respx.mock
async def test_ai_mode_location_errors_raise_validation_error():
    detail = "Use only one of location, uule, or lat/lon."
    respx.get(AI_MODE).mock(return_value=httpx.Response(422, json={"detail": detail}))
    async with ScrapeBadger(api_key="test", base_url="https://example.test") as client:
        with pytest.raises(ValidationError, match="only one of"):
            await client.google.ai_mode.search("cafe", location="Seoul", lat=1.0, lon=2.0)
