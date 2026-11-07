"""Exercise the generated Yelp client through the public SDK and HTTP transport."""

from __future__ import annotations

from typing import Any

import httpx
import respx

from scrapebadger import ScrapeBadger

BASE = "https://api.test.scrapebadger.com"


def _business(position: int, **overrides: Any) -> dict[str, Any]:
    business: dict[str, Any] = {
        "position": position,
        "is_ad": False,
        "id": f"biz-{position}",
        "alias": f"pizza-place-{position}-san-francisco",
        "name": f"Pizza Place {position}",
        "url": f"https://www.yelp.com/biz/pizza-place-{position}-san-francisco",
        "rating": 4.5,
        "review_count": 0,
        "price": None,
        "price_level": None,
        "categories": [{"alias": "pizza", "title": "Pizza"}],
        "neighborhoods": [],
        "address": None,
        "city": "San Francisco",
        "phone": None,
        "timezone": "America/Los_Angeles",
        "opening_hours": [],
        "snippet": None,
        "snippet_type": None,
        "highlights": [],
        "tags": [],
        "photos": [],
        "alternate_names": [],
        "is_service_area_business": False,
        "is_yelp_guaranteed": False,
        "has_verified_license": False,
        "ad_placement": None,
    }
    business.update(overrides)
    return business


@respx.mock
async def test_search_sends_every_filter_and_keeps_native_payload(client: ScrapeBadger) -> None:
    # Ads stay separate from ranked results; false, zero, empty and null values
    # inside nested groups must arrive unchanged.
    payload: dict[str, Any] = {
        "market": "ca",
        "query": "pizza",
        "location": "Toronto, ON",
        "location_resolved": {
            "city": "Toronto",
            "state": "ON",
            "country": "CA",
            "latitude": 43.65,
            "longitude": -79.38,
        },
        "did_you_mean": None,
        "query_matched": True,
        "total_results": 240,
        "page": 2,
        "page_size": 10,
        "total_pages": 11,
        "has_next_page": True,
        "next_page": 3,
        "results": [_business(11), _business(12, rating=None, review_count=None)],
        "ads": [_business(0, is_ad=True, ad_placement="top")],
        "filters": {
            "price": {
                "title": "Price",
                "type": "multi",
                "options": [
                    {"value": "1", "text": "$", "selected": False},
                    {"value": "2", "text": "$$", "selected": True},
                ],
            },
            "features": {"title": "Features", "type": "multi", "options": []},
        },
        "related_searches": [],
        "source_url": "https://www.yelp.ca/search?find_desc=pizza&find_loc=Toronto%2C+ON&start=10",
        "fetched_at": "2026-11-07T16:00:00Z",
        "fetched_utc": 1794067200.0,
    }
    route = respx.get(f"{BASE}/v1/yelp/search").mock(
        return_value=httpx.Response(200, json=payload, headers={"X-Credits-Used": "15"})
    )

    result = await client.yelp.search_businesses(
        location="Toronto, ON",
        query="pizza",
        market="ca",
        category="pizza",
        sort_by="review_count",
        price="1,2",
        features="delivery,takeout",
        page=2,
    )

    assert route.call_count == 1
    request = route.calls.last.request
    assert dict(request.url.params) == {
        "location": "Toronto, ON",
        "query": "pizza",
        "market": "ca",
        "category": "pizza",
        "sort_by": "review_count",
        "price": "1,2",
        "features": "delivery,takeout",
        "page": "2",
    }
    assert request.headers["x-api-key"] == "test_api_key_12345"
    assert result == payload


@respx.mock
async def test_search_defaults_and_genuine_empty_result(client: ScrapeBadger) -> None:
    # A genuine empty search is a normal 200 response, not an error or a
    # fabricated fallback; the SDK must not coerce its zeros and nulls.
    payload: dict[str, Any] = {
        "market": "us",
        "query": None,
        "location": "Barrow, AK",
        "location_resolved": {
            "city": "Utqiagvik",
            "state": "AK",
            "country": "US",
            "latitude": None,
            "longitude": None,
        },
        "did_you_mean": None,
        "query_matched": False,
        "total_results": 0,
        "page": 1,
        "page_size": 10,
        "total_pages": 0,
        "has_next_page": False,
        "next_page": None,
        "results": [],
        "ads": [],
        "filters": {},
        "related_searches": [],
        "source_url": "https://www.yelp.com/search?find_loc=Barrow%2C+AK&cflt=pizza",
        "fetched_at": "2026-11-07T16:00:00Z",
        "fetched_utc": 1794067200.0,
    }
    route = respx.get(f"{BASE}/v1/yelp/search").mock(return_value=httpx.Response(200, json=payload))

    result = await client.yelp.search_businesses(location="Barrow, AK", category="pizza")

    assert dict(route.calls.last.request.url.params) == {
        "location": "Barrow, AK",
        "market": "us",
        "category": "pizza",
        "sort_by": "recommended",
        "page": "1",
    }
    assert result == payload


@respx.mock
async def test_markets_use_no_query_and_keep_payload(client: ScrapeBadger) -> None:
    payload = {
        "markets": [
            {
                "code": "us",
                "name": "United States",
                "domain": "www.yelp.com",
                "language": "en",
                "currency": "USD",
            },
            {
                "code": "ca",
                "name": "Canada",
                "domain": "www.yelp.ca",
                "language": "en",
                "currency": "CAD",
            },
        ]
    }
    route = respx.get(f"{BASE}/v1/yelp/markets").mock(
        return_value=httpx.Response(200, json=payload)
    )

    result = await client.yelp.list_markets()

    assert route.calls.last.request.url.query == b""
    assert result == payload
