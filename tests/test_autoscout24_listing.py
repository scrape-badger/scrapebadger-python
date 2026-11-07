"""Exercise the listing handoff through the public SDK and HTTP transport."""

from __future__ import annotations

from typing import Any

import httpx
import pytest
import respx

from scrapebadger import ScrapeBadger

BASE = "https://api.test.scrapebadger.com"
LISTING_ID = "3124825e-43e6-45d4-8987-775b827fb166"
LISTING_URL = f"https://www.autoscout24.be/fr/offres/volkswagen-golf-{LISTING_ID}"


@pytest.mark.parametrize(
    "lookup",
    [
        {"url": LISTING_URL},
        {"listing_id": LISTING_ID, "market": "be"},
    ],
)
@respx.mock
async def test_listing_handoff_preserves_market_and_native_data(
    client: ScrapeBadger, lookup: dict[str, str]
) -> None:
    # Native vehicle/equipment groups are intentionally raw, including values
    # that must survive without a typed model dropping or coercing them.
    payload: dict[str, Any] = {
        "market": "be",
        "source_url": LISTING_URL,
        "listing": {
            "id": LISTING_ID,
            "title": "Volkswagen Golf",
            "price": 10850,
            "currency": "EUR",
            "vehicle": {"rawPowerInKw": 81, "isDamaged": False, "previousOwners": 0},
            "equipment": {"comfortAndConvenience": [{"categoryName": "Confort"}]},
        },
        "latency_ms": 1397,
    }
    route = respx.get(f"{BASE}/v1/autoscout24/listing").mock(
        return_value=httpx.Response(200, json=payload, headers={"X-Credits-Used": "10"})
    )

    result = await client.autoscout24.get_listing(**lookup)

    assert route.call_count == 1
    request = route.calls.last.request
    assert dict(request.url.params) == lookup
    assert request.headers["x-api-key"] == "test_api_key_12345"
    assert result == payload
