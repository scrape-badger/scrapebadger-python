"""Unit tests for Redfin SDK methods and models.

Tests cover:
- TestRedfinModels: Pydantic model construction, validation, immutability
- TestRedfinClient: endpoint routing via a mocked HTTP client
- TestRedfinImports: public API importability
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from scrapebadger.redfin.client import RedfinClient
from scrapebadger.redfin.models import (
    AgentResponse,
    AutocompleteResponse,
    MarketsResponse,
    Property,
    PropertyResponse,
    SearchResponse,
)

# ---------------------------------------------------------------------------
# Shared sample data
# ---------------------------------------------------------------------------

SAMPLE_LISTING: dict[str, Any] = {
    "position": 1,
    "property_id": 12345678,
    "url": "https://www.redfin.com/TX/Austin/123-Main-St/home/12345678",
    "mls_status": "Active",
    "price": 750000,
    "beds": 3.0,
    "baths": 2.5,
    "sqft": 2100,
    "street_line": "123 Main St",
    "city": "Austin",
    "state": "TX",
    "zip": "78701",
    "latitude": 30.2672,
    "longitude": -97.7431,
    "days_on_market": 5,
}

SAMPLE_PROPERTY: dict[str, Any] = {
    "property_id": 12345678,
    "url": "https://www.redfin.com/TX/Austin/123-Main-St/home/12345678",
    "mls_status": "Active",
    "price": 750000,
    "beds": 3.0,
    "baths": 2.5,
    "sqft": 2100,
    "address": {
        "street_address": "123 Main St",
        "city": "Austin",
        "state": "TX",
        "zip": "78701",
    },
    "schools": [{"name": "Austin High", "rating": 8, "level": "high"}],
    "price_history": [{"event": "Listed", "price": 750000}],
}

SAMPLE_AGENT: dict[str, Any] = {
    "agent_id": "jane-doe",
    "name": "Jane Doe",
    "url": "https://www.redfin.com/real-estate-agents/jane-doe",
    "rating": 4.9,
    "review_count": 42,
    "listings": [SAMPLE_LISTING],
}

SEARCH_RESPONSE: dict[str, Any] = {
    "location": "Austin, TX",
    "status": "for_sale",
    "results": [SAMPLE_LISTING],
    "total_results": 1234,
    "pagination": {"current_page": 1, "per_page": 40, "total_results": 1234},
}

PROPERTY_RESPONSE: dict[str, Any] = {"property": SAMPLE_PROPERTY}
AGENT_RESPONSE: dict[str, Any] = {"agent": SAMPLE_AGENT}
AUTOCOMPLETE_RESPONSE: dict[str, Any] = {
    "query": "austin",
    "results": [{"name": "Austin, TX", "display_name": "Austin, TX", "type": "city"}],
}
MARKETS_RESPONSE: dict[str, Any] = {
    "markets": [
        {
            "code": "us",
            "country": "US",
            "currency": "USD",
            "locale": "en-US",
            "name": "Redfin United States",
            "domain": "redfin.com",
        }
    ]
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_base_client() -> MagicMock:
    """Return a mock BaseClient with AsyncMock methods."""
    client = MagicMock()
    client.get = AsyncMock()
    client.post = AsyncMock()
    return client


@pytest.fixture
def redfin_client(mock_base_client: MagicMock) -> RedfinClient:
    return RedfinClient(mock_base_client)


# ===========================================================================
# TestRedfinModels
# ===========================================================================


class TestRedfinModels:
    def test_property_full(self) -> None:
        prop = Property.model_validate(SAMPLE_PROPERTY)
        assert prop.property_id == 12345678
        assert prop.price == 750000
        assert prop.address is not None
        assert prop.address.city == "Austin"
        assert len(prop.schools) == 1
        assert prop.schools[0].rating == 8
        assert len(prop.price_history) == 1

    def test_property_is_frozen(self) -> None:
        prop = Property.model_validate(SAMPLE_PROPERTY)
        with pytest.raises(Exception):  # noqa: B017
            prop.price = 1  # type: ignore[misc]

    def test_search_response(self) -> None:
        resp = SearchResponse.model_validate(SEARCH_RESPONSE)
        assert resp.total_results == 1234
        assert len(resp.results) == 1
        assert resp.results[0].property_id == 12345678
        assert resp.pagination.current_page == 1

    def test_search_response_defaults(self) -> None:
        resp = SearchResponse.model_validate({})
        assert resp.results == []
        assert resp.status == "for_sale"
        assert resp.total_results == 0

    def test_property_response(self) -> None:
        resp = PropertyResponse.model_validate(PROPERTY_RESPONSE)
        assert resp.property.property_id == 12345678

    def test_agent_response(self) -> None:
        resp = AgentResponse.model_validate(AGENT_RESPONSE)
        assert resp.agent.agent_id == "jane-doe"
        assert resp.agent.review_count == 42
        assert len(resp.agent.listings) == 1

    def test_autocomplete_response(self) -> None:
        resp = AutocompleteResponse.model_validate(AUTOCOMPLETE_RESPONSE)
        assert resp.query == "austin"
        assert len(resp.results) == 1
        assert resp.results[0].name == "Austin, TX"

    def test_markets_response(self) -> None:
        resp = MarketsResponse.model_validate(MARKETS_RESPONSE)
        assert len(resp.markets) == 1
        assert resp.markets[0].code == "us"

    def test_ignores_unknown_fields(self) -> None:
        resp = MarketsResponse.model_validate({"markets": [], "unexpected": 123})
        assert resp.markets == []


# ===========================================================================
# TestRedfinClient
# ===========================================================================


class TestRedfinClient:
    async def test_search_default_params(
        self, redfin_client: RedfinClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = SEARCH_RESPONSE
        result = await redfin_client.search("Austin, TX")

        assert isinstance(result, SearchResponse)
        call_args = mock_base_client.get.call_args
        assert call_args[0][0] == "/v1/redfin/search"
        params = call_args[1]["params"]
        assert params["location"] == "Austin, TX"
        assert params["page"] == 1
        assert params["sort"] is None
        assert params["price_min"] is None

    async def test_search_with_filters(
        self, redfin_client: RedfinClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = SEARCH_RESPONSE
        await redfin_client.search(
            "Austin, TX",
            page=2,
            sort="price_low_to_high",
            price_min=100000,
            price_max=750000,
            beds_min=3,
            baths_min=2.0,
            home_type="house",
            max_days_on_market=30,
        )
        params = mock_base_client.get.call_args[1]["params"]
        assert params["page"] == 2
        assert params["sort"] == "price_low_to_high"
        assert params["price_max"] == 750000
        assert params["beds_min"] == 3
        assert params["home_type"] == "house"
        assert params["max_days_on_market"] == 30

    async def test_get_property_by_id(
        self, redfin_client: RedfinClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = PROPERTY_RESPONSE
        result = await redfin_client.get_property("12345678")
        assert isinstance(result, PropertyResponse)
        mock_base_client.get.assert_called_once_with("/v1/redfin/property/12345678")

    async def test_get_property_by_url(
        self, redfin_client: RedfinClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = PROPERTY_RESPONSE
        url = "https://www.redfin.com/TX/Austin/123-Main-St/home/12345678"
        result = await redfin_client.get_property(url=url)
        assert isinstance(result, PropertyResponse)
        call_args = mock_base_client.get.call_args
        assert call_args[0][0] == "/v1/redfin/property"
        assert call_args[1]["params"] == {"url": url}

    async def test_get_agent(
        self, redfin_client: RedfinClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = AGENT_RESPONSE
        result = await redfin_client.get_agent("jane-doe")
        assert isinstance(result, AgentResponse)
        call_args = mock_base_client.get.call_args
        assert call_args[0][0] == "/v1/redfin/agent"
        params = call_args[1]["params"]
        assert params["agent_id"] == "jane-doe"
        assert params["url"] is None

    async def test_get_agent_by_url(
        self, redfin_client: RedfinClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = AGENT_RESPONSE
        url = "https://www.redfin.com/real-estate-agents/jane-doe"
        await redfin_client.get_agent(url=url)
        params = mock_base_client.get.call_args[1]["params"]
        assert params["agent_id"] is None
        assert params["url"] == url

    async def test_autocomplete(
        self, redfin_client: RedfinClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = AUTOCOMPLETE_RESPONSE
        result = await redfin_client.autocomplete("austin")
        assert isinstance(result, AutocompleteResponse)
        call_args = mock_base_client.get.call_args
        assert call_args[0][0] == "/v1/redfin/autocomplete"
        assert call_args[1]["params"] == {"query": "austin"}

    async def test_list_markets(
        self, redfin_client: RedfinClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = MARKETS_RESPONSE
        result = await redfin_client.list_markets()
        assert isinstance(result, MarketsResponse)
        mock_base_client.get.assert_called_once_with("/v1/redfin/markets")


# ===========================================================================
# TestRedfinImports
# ===========================================================================


class TestRedfinImports:
    def test_client_importable(self) -> None:
        from scrapebadger.redfin import RedfinClient as _  # noqa: F401

    def test_client_top_level_importable(self) -> None:
        from scrapebadger import RedfinClient as _  # noqa: F401

    def test_property_top_level_importable(self) -> None:
        from scrapebadger import RedfinProperty as _  # noqa: F401

    def test_search_response_importable(self) -> None:
        from scrapebadger.redfin import SearchResponse as _  # noqa: F401
