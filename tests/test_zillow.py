"""Unit tests for Zillow SDK methods and models.

Tests cover:
- TestZillowModels: Pydantic model construction and validation
- TestZillowClient: ZillowClient sub-client wiring
- TestRouting: endpoint routing (path + params) via a mocked HTTP client
- TestZillowImports: public API importability
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from scrapebadger.zillow.agent import AgentClient
from scrapebadger.zillow.client import ZillowClient
from scrapebadger.zillow.models import (
    Agent,
    AutocompleteResponse,
    MarketInfo,
    MarketsResponse,
    Property,
    SearchResponse,
)
from scrapebadger.zillow.properties import PropertiesClient
from scrapebadger.zillow.reference import ReferenceClient
from scrapebadger.zillow.search import SearchClient


class TestZillowModels:
    def test_search_response_from_payload(self) -> None:
        r = SearchResponse.model_validate(
            {
                "location": "Austin, TX",
                "status": "for_sale",
                "results": [{"position": 1, "zpid": "1", "price": 500000}],
                "map_results_count": 42,
            }
        )
        assert r.location == "Austin, TX"
        assert r.results[0].zpid == "1"
        assert r.map_results_count == 42

    def test_property_requires_zpid(self) -> None:
        with pytest.raises(ValueError):
            Property.model_validate({})

    def test_property_nested_home_facts(self) -> None:
        p = Property.model_validate(
            {"zpid": "9", "home_facts": {"has_garage": True, "heating": ["Forced Air"]}}
        )
        assert p.home_facts is not None
        assert p.home_facts.has_garage is True
        assert p.home_facts.heating == ["Forced Air"]

    def test_agent_all_optional(self) -> None:
        assert Agent.model_validate({}).name is None

    def test_market_info_required(self) -> None:
        with pytest.raises(ValueError):
            MarketInfo.model_validate({"code": "us"})  # missing required fields


class TestZillowClient:
    def test_subclient_wiring(self) -> None:
        c = ZillowClient(MagicMock())
        assert isinstance(c.search, SearchClient)
        assert isinstance(c.properties, PropertiesClient)
        assert isinstance(c.agents, AgentClient)
        assert isinstance(c.reference, ReferenceClient)


class TestRouting:
    @pytest.mark.asyncio
    async def test_search_routes(self) -> None:
        http = MagicMock()
        http.get = AsyncMock(return_value={"location": "Austin, TX", "results": []})
        out = await SearchClient(http).search("Austin, TX", beds_min=3, sort="newest")
        path, kwargs = http.get.call_args[0][0], http.get.call_args[1]
        assert path == "/v1/zillow/search"
        assert kwargs["params"]["location"] == "Austin, TX"
        assert kwargs["params"]["beds_min"] == 3
        assert kwargs["params"]["sort"] == "newest"
        assert isinstance(out, SearchResponse)

    @pytest.mark.asyncio
    async def test_autocomplete_routes(self) -> None:
        http = MagicMock()
        http.get = AsyncMock(return_value={"query": "austin", "results": []})
        out = await SearchClient(http).autocomplete("austin")
        assert http.get.call_args[0][0] == "/v1/zillow/autocomplete"
        assert isinstance(out, AutocompleteResponse)

    @pytest.mark.asyncio
    async def test_property_routes(self) -> None:
        http = MagicMock()
        http.get = AsyncMock(return_value={"property": {"zpid": "42"}})
        out = await PropertiesClient(http).get_property("42")
        assert http.get.call_args[0][0] == "/v1/zillow/property/42"
        assert isinstance(out, Property)
        assert out.zpid == "42"

    @pytest.mark.asyncio
    async def test_agent_routes(self) -> None:
        http = MagicMock()
        http.get = AsyncMock(return_value={"agent": {"name": "Jane Doe"}})
        out = await AgentClient(http).get_agent(username="jane-doe")
        path, kwargs = http.get.call_args[0][0], http.get.call_args[1]
        assert path == "/v1/zillow/agent"
        assert kwargs["params"]["username"] == "jane-doe"
        assert isinstance(out, Agent)
        assert out.name == "Jane Doe"

    @pytest.mark.asyncio
    async def test_markets_routes(self) -> None:
        http = MagicMock()
        http.get = AsyncMock(return_value={"markets": []})
        out = await ReferenceClient(http).list_markets()
        assert http.get.call_args[0][0] == "/v1/zillow/markets"
        assert isinstance(out, MarketsResponse)


class TestZillowImports:
    def test_public_api(self) -> None:
        from scrapebadger import ZillowClient as ExportedClient
        from scrapebadger import ZillowSearchResponse

        assert ExportedClient is ZillowClient
        assert ZillowSearchResponse is SearchResponse
