"""Unit tests for Realtor SDK methods and models.

Tests cover:
- TestRealtorModels: Pydantic model construction and validation
- TestRealtorClient: RealtorClient sub-client wiring
- TestSearchClient / TestPropertiesClient / TestReferenceClient: endpoint
  routing (path + params) via a mocked HTTP client
- TestRealtorImports: public API importability
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from scrapebadger.realtor.client import RealtorClient
from scrapebadger.realtor.models import (
    AutocompleteResponse,
    MarketInfo,
    MarketsResponse,
    PropertyDetail,
    SearchResponse,
)
from scrapebadger.realtor.properties import PropertiesClient
from scrapebadger.realtor.reference import ReferenceClient
from scrapebadger.realtor.search import SearchClient


class TestRealtorModels:
    def test_search_response_from_payload(self) -> None:
        r = SearchResponse.model_validate(
            {
                "market": "us",
                "total": 2,
                "page": 1,
                "results": [{"property_id": "1", "list_price": 500000}],
            }
        )
        assert r.market == "us"
        assert r.results[0].property_id == "1"

    def test_property_detail_all_optional(self) -> None:
        assert PropertyDetail.model_validate({}).property_id is None

    def test_market_info_required(self) -> None:
        with pytest.raises(ValueError):
            MarketInfo.model_validate({"code": "us"})  # missing required fields


class TestRealtorClient:
    def test_subclient_wiring(self) -> None:
        c = RealtorClient(MagicMock())
        assert isinstance(c.search, SearchClient)
        assert isinstance(c.properties, PropertiesClient)
        assert isinstance(c.reference, ReferenceClient)


class TestRouting:
    @pytest.mark.asyncio
    async def test_search_routes(self) -> None:
        http = MagicMock()
        http.get = AsyncMock(return_value={"market": "us", "results": []})
        out = await SearchClient(http).search("Austin, TX", market="us", beds_min=3)
        path, kwargs = http.get.call_args[0][0], http.get.call_args[1]
        assert path == "/v1/realtor/search"
        assert kwargs["params"]["location"] == "Austin, TX"
        assert kwargs["params"]["beds_min"] == 3
        assert isinstance(out, SearchResponse)

    @pytest.mark.asyncio
    async def test_autocomplete_routes(self) -> None:
        http = MagicMock()
        http.get = AsyncMock(return_value={"market": "ca", "query": "toronto", "suggestions": []})
        out = await SearchClient(http).autocomplete("toronto", market="ca")
        assert http.get.call_args[0][0] == "/v1/realtor/autocomplete"
        assert isinstance(out, AutocompleteResponse)

    @pytest.mark.asyncio
    async def test_property_routes(self) -> None:
        http = MagicMock()
        http.get = AsyncMock(return_value={"property_id": "42"})
        out = await PropertiesClient(http).get_property("42", market="us")
        assert http.get.call_args[0][0] == "/v1/realtor/properties/42"
        assert isinstance(out, PropertyDetail)

    @pytest.mark.asyncio
    async def test_markets_routes(self) -> None:
        http = MagicMock()
        http.get = AsyncMock(return_value={"markets": []})
        out = await ReferenceClient(http).list_markets()
        assert http.get.call_args[0][0] == "/v1/realtor/markets"
        assert isinstance(out, MarketsResponse)


class TestRealtorImports:
    def test_public_api(self) -> None:
        from scrapebadger import RealtorClient as ExportedClient
        from scrapebadger import RealtorSearchResponse

        assert ExportedClient is RealtorClient
        assert RealtorSearchResponse is SearchResponse
