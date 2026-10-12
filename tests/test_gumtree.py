"""Unit tests for Gumtree SDK methods and models.

Tests cover:
- TestGumtreeClient: wiring on ScrapeBadger
- TestRouting: every one of the 9 endpoints routes to the right path/params,
  and `market` is passed through (unset = the server default, uk)
- TestGumtreeModels: real API responses (tests/fixtures/gumtree_samples.json,
  uk + au + za) parse into the models with no field silently dropped,
  immutability
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import BaseModel

from scrapebadger.gumtree.client import GumtreeClient
from scrapebadger.gumtree.models import (
    AutocompleteResponse,
    FiltersResponse,
    ListingDetail,
    LocationAutocompleteResponse,
    MarketsResponse,
    SearchResponse,
    SellerListingsResponse,
    TreeResponse,
)

SAMPLES: dict[str, Any] = json.loads(
    (Path(__file__).parent / "fixtures" / "gumtree_samples.json").read_text(encoding="utf-8")
)
SEARCH = SAMPLES["GET /v1/gumtree/search?category=cars"]
LISTING = SAMPLES["GET /v1/gumtree/listings/1803293391"]
FILTERS = SAMPLES["GET /v1/gumtree/search/filters?category=cars"]
SELLER_LISTINGS = SAMPLES["GET /v1/gumtree/listings/1803293391/seller-listings"]
AUTOCOMPLETE = SAMPLES["GET /v1/gumtree/autocomplete?query=sofa"]
LOCATION_AUTOCOMPLETE = SAMPLES["GET /v1/gumtree/locations/autocomplete?query=leed"]
CATEGORIES = SAMPLES["GET /v1/gumtree/categories?parent_id=2551"]
LOCATIONS = SAMPLES["GET /v1/gumtree/locations?parent_id=10000393"]
MARKETS = SAMPLES["GET /v1/gumtree/markets"]
ZA_SEARCH = SAMPLES["GET /v1/gumtree/search?market=za&category=9077&location=3100003"]
ZA_LISTING = SAMPLES["GET /v1/gumtree/listings/10013681289561010209976109?market=za"]
AU_SEARCH = SAMPLES["GET /v1/gumtree/search?market=au"]
AU_LISTING = SAMPLES["GET /v1/gumtree/listings/1339574407?market=au"]
ZA_LISTING_ID = "10013681289561010209976109"


@pytest.fixture
def mock_base_client() -> MagicMock:
    """Return a mock BaseClient with AsyncMock methods."""
    client = MagicMock()
    client.get = AsyncMock()
    return client


@pytest.fixture
def gumtree(mock_base_client: MagicMock) -> GumtreeClient:
    return GumtreeClient(mock_base_client)


def _call(mock_base_client: MagicMock) -> tuple[str, dict[str, Any] | None]:
    args, kwargs = mock_base_client.get.call_args
    return args[0], kwargs.get("params")


class TestGumtreeClient:
    def test_exposed_on_main_client(self) -> None:
        from scrapebadger import GumtreeClient as Exported
        from scrapebadger import ScrapeBadger

        client = ScrapeBadger(api_key="test-key")
        assert isinstance(client.gumtree, GumtreeClient)
        assert client.gumtree is client.gumtree
        assert Exported is GumtreeClient


class TestRouting:
    async def test_search_defaults(
        self, gumtree: GumtreeClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = SEARCH
        result = await gumtree.search()

        assert isinstance(result, SearchResponse)
        path, params = _call(mock_base_client)
        assert path == "/v1/gumtree/search"
        assert params == {
            "query": None,
            "category": "all",
            "location": None,
            "distance": None,
            "min_price": None,
            "max_price": None,
            "sort": None,
            "seller_type": None,
            "urgent_only": None,
            "with_photos": None,
            "filters": None,
            "page": 1,
            "market": None,
        }

    async def test_search_all_params(
        self, gumtree: GumtreeClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = SEARCH
        await gumtree.search(
            "bmw 3 series",
            category="cars",
            location="SW1A 1AA",
            distance=25,
            min_price=1000,
            max_price=9000,
            sort="price_asc",
            seller_type="private",
            urgent_only=True,
            with_photos=True,
            filters="vehicle_make:bmw,vehicle_fuel_type:petrol",
            page=3,
        )

        path, params = _call(mock_base_client)
        assert path == "/v1/gumtree/search"
        assert params == {
            "query": "bmw 3 series",
            "category": "cars",
            "location": "SW1A 1AA",
            "distance": 25,
            "min_price": 1000,
            "max_price": 9000,
            "sort": "price_asc",
            "seller_type": "private",
            "urgent_only": True,
            "with_photos": True,
            "filters": "vehicle_make:bmw,vehicle_fuel_type:petrol",
            "page": 3,
            "market": None,
        }

    async def test_search_market(self, gumtree: GumtreeClient, mock_base_client: MagicMock) -> None:
        mock_base_client.get.return_value = ZA_SEARCH
        result = await gumtree.search(
            market="za", category="9077", location="3100003", filters="ma:toyota"
        )

        assert result.market == "za"
        path, params = _call(mock_base_client)
        assert path == "/v1/gumtree/search"
        assert params is not None
        assert params["market"] == "za"
        assert params["category"] == "9077"
        assert params["location"] == "3100003"
        assert params["filters"] == "ma:toyota"

    async def test_search_filters(
        self, gumtree: GumtreeClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = FILTERS
        result = await gumtree.search_filters("cars", location="leeds", query="diesel")

        assert isinstance(result, FiltersResponse)
        assert _call(mock_base_client) == (
            "/v1/gumtree/search/filters",
            {
                "category": "cars",
                "location": "leeds",
                "query": "diesel",
                "filters": None,
                "market": None,
            },
        )

    async def test_search_filters_market(
        self, gumtree: GumtreeClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = FILTERS
        await gumtree.search_filters("9077", filters="ma:toyota", market="za")

        assert _call(mock_base_client) == (
            "/v1/gumtree/search/filters",
            {
                "category": "9077",
                "location": None,
                "query": None,
                "filters": "ma:toyota",
                "market": "za",
            },
        )

    async def test_get_listing(self, gumtree: GumtreeClient, mock_base_client: MagicMock) -> None:
        mock_base_client.get.return_value = LISTING
        result = await gumtree.get_listing("1803293391")

        assert isinstance(result, ListingDetail)
        assert _call(mock_base_client) == ("/v1/gumtree/listings/1803293391", {"market": None})

    async def test_get_listing_market(
        self, gumtree: GumtreeClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = ZA_LISTING
        result = await gumtree.get_listing(ZA_LISTING_ID, market="za")

        assert result.market == "za"
        assert _call(mock_base_client) == (
            f"/v1/gumtree/listings/{ZA_LISTING_ID}",
            {"market": "za"},
        )

    async def test_get_seller_listings(
        self, gumtree: GumtreeClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = SELLER_LISTINGS
        result = await gumtree.get_seller_listings("1803293391", page=2)

        assert isinstance(result, SellerListingsResponse)
        assert _call(mock_base_client) == (
            "/v1/gumtree/listings/1803293391/seller-listings",
            {"page": 2, "market": None},
        )

    async def test_autocomplete(self, gumtree: GumtreeClient, mock_base_client: MagicMock) -> None:
        mock_base_client.get.return_value = AUTOCOMPLETE
        result = await gumtree.autocomplete("sofa")

        assert isinstance(result, AutocompleteResponse)
        assert _call(mock_base_client) == (
            "/v1/gumtree/autocomplete",
            {"query": "sofa", "market": None},
        )

    async def test_location_autocomplete(
        self, gumtree: GumtreeClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = LOCATION_AUTOCOMPLETE
        result = await gumtree.location_autocomplete("leed")

        assert isinstance(result, LocationAutocompleteResponse)
        assert _call(mock_base_client) == (
            "/v1/gumtree/locations/autocomplete",
            {"query": "leed", "market": None},
        )

    async def test_list_locations(
        self, gumtree: GumtreeClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = LOCATIONS
        result = await gumtree.list_locations(10000393)

        assert isinstance(result, TreeResponse)
        assert _call(mock_base_client) == (
            "/v1/gumtree/locations",
            {"parent_id": 10000393, "market": None},
        )

    async def test_list_categories_default_root(
        self, gumtree: GumtreeClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = CATEGORIES
        result = await gumtree.list_categories()

        assert isinstance(result, TreeResponse)
        # None is dropped by BaseClient, so the server defaults (the uk root) apply.
        assert _call(mock_base_client) == (
            "/v1/gumtree/categories",
            {"parent_id": None, "market": None},
        )

    @pytest.mark.parametrize(
        ("method", "args", "path", "params"),
        [
            (
                "get_seller_listings",
                (ZA_LISTING_ID,),
                f"/v1/gumtree/listings/{ZA_LISTING_ID}/seller-listings",
                {"page": 1, "market": "au"},
            ),
            (
                "autocomplete",
                ("bik",),
                "/v1/gumtree/autocomplete",
                {"query": "bik", "market": "au"},
            ),
            (
                "location_autocomplete",
                ("sydney",),
                "/v1/gumtree/locations/autocomplete",
                {"query": "sydney", "market": "au"},
            ),
            ("list_locations", (), "/v1/gumtree/locations", {"parent_id": None, "market": "au"}),
            (
                "list_categories",
                (9299,),
                "/v1/gumtree/categories",
                {"parent_id": 9299, "market": "au"},
            ),
        ],
    )
    async def test_market_passed_through(
        self,
        gumtree: GumtreeClient,
        mock_base_client: MagicMock,
        method: str,
        args: tuple[Any, ...],
        path: str,
        params: dict[str, Any],
    ) -> None:
        mock_base_client.get.return_value = {"query": "x", "listing_id": "1", "id": 1}
        await getattr(gumtree, method)(*args, market="au")

        assert _call(mock_base_client) == (path, params)

    async def test_list_markets(self, gumtree: GumtreeClient, mock_base_client: MagicMock) -> None:
        mock_base_client.get.return_value = MARKETS
        result = await gumtree.list_markets()

        assert isinstance(result, MarketsResponse)
        assert _call(mock_base_client) == ("/v1/gumtree/markets", None)
        assert [m.market for m in result.markets] == ["uk", "au", "za"]
        za = result.markets[2]
        assert (za.domain, za.currency, za.distance_unit, za.page_size) == (
            "www.gumtree.co.za",
            "ZAR",
            None,
            20,
        )


def _assert_round_trips(payload: Any, dumped: Any, path: str = "$") -> None:
    """Every key and value in the API payload must survive model parsing.

    `extra="ignore"` drops undeclared fields silently, so this is what pins
    the models to the real response shape.
    """
    if isinstance(payload, dict):
        assert isinstance(dumped, dict), path
        for key, value in payload.items():
            assert key in dumped, f"{path}.{key} dropped by the model"
            _assert_round_trips(value, dumped[key], f"{path}.{key}")
    elif isinstance(payload, list):
        assert isinstance(dumped, list), path
        assert len(payload) == len(dumped), path
        for i, (p, d) in enumerate(zip(payload, dumped, strict=True)):
            _assert_round_trips(p, d, f"{path}[{i}]")
    else:
        assert payload == dumped, f"{path}: {payload!r} != {dumped!r}"


class TestGumtreeModels:
    @pytest.mark.parametrize(
        ("model", "payload"),
        [
            (SearchResponse, SEARCH),
            (ListingDetail, LISTING),
            (FiltersResponse, FILTERS),
            (SellerListingsResponse, SELLER_LISTINGS),
            (AutocompleteResponse, AUTOCOMPLETE),
            (LocationAutocompleteResponse, LOCATION_AUTOCOMPLETE),
            (TreeResponse, CATEGORIES),
            (TreeResponse, LOCATIONS),
            (MarketsResponse, MARKETS),
            (SearchResponse, ZA_SEARCH),
            (ListingDetail, ZA_LISTING),
            (SearchResponse, AU_SEARCH),
            (ListingDetail, AU_LISTING),
        ],
    )
    def test_real_responses_round_trip(self, model: type[BaseModel], payload: Any) -> None:
        _assert_round_trips(payload, model.model_validate(payload).model_dump())

    def test_listing_detail_nesting(self) -> None:
        listing = ListingDetail.model_validate(LISTING)

        assert listing.price == 5699.0
        assert listing.currency == "GBP"
        assert listing.breadcrumbs[1].name == "Motors"
        assert listing.attributes[0].key == "vehicle_make"
        assert listing.seller is not None
        assert listing.seller.type == "Trade"
        assert listing.seller.rating is not None
        assert listing.seller.rating.breakdown["5"] == 0
        assert listing.seller.verification is not None
        assert listing.seller.verification.status == "VERIFIED"

    def test_uk_responses_default_to_uk(self) -> None:
        search = SearchResponse.model_validate(SEARCH)
        assert (search.market, search.currency) == ("uk", "GBP")
        # A response without the new fields (pre-0.60 API) still parses as uk.
        legacy = SearchResponse.model_validate({"page": 1})
        assert (legacy.market, legacy.currency) == ("uk", "GBP")

    def test_za_fields(self) -> None:
        search = SearchResponse.model_validate(ZA_SEARCH)
        assert (search.market, search.currency, search.total_results) == ("za", "ZAR", 2964)
        car = search.listings[0]
        assert car.id == "10013681279811013062940409"
        assert car.short_id == "1368127981"
        assert car.price == 248000
        assert car.price_type == "FIXED"
        assert car.seller_name == "Kevin Noel Ngandu"
        assert search.listings[1].price_type == "MAKE_OFFER"

        listing = ListingDetail.model_validate(ZA_LISTING)
        assert listing.market == "za"
        assert (listing.price_type, listing.status, listing.view_count) == ("FIXED", "ACTIVE", 65)
        assert listing.seller is not None
        assert listing.seller.lifetime_listings == 3100
        assert listing.seller.total_views == 263430
        assert listing.seller.phone_masked == "068*******"

    def test_au_fields(self) -> None:
        search = SearchResponse.model_validate(AU_SEARCH)
        assert (search.market, search.currency) == ("au", "AUD")
        assert search.listings[0].seller_name == "Canning Vale Toyota"
        assert search.category_facets[0].id == 9299
        assert search.category_facets[0].name == "Cars & Vehicles"

        listing = ListingDetail.model_validate(AU_LISTING)
        assert (listing.market, listing.currency, listing.price) == ("au", "AUD", 15.95)
        assert (listing.view_count, listing.reply_count) == (88, 0)
        assert listing.seller is not None
        assert listing.seller.member_since_year == 2025
        assert listing.seller.last_active_text == "yesterday"

    def test_filters_and_trees(self) -> None:
        filters = FiltersResponse.model_validate(FILTERS)
        assert filters.filters[0].key == "vehicle_make"
        assert filters.filters[0].options[0].count is not None
        assert filters.sort_options[0].value == "relevance"

        categories = TreeResponse.model_validate(CATEGORIES)
        assert categories.id == 2551
        assert any(child.slug == "cars" for child in categories.children)

    def test_models_are_frozen_and_ignore_unknown_fields(self) -> None:
        listing = ListingDetail.model_validate({"id": "1", "a_new_gumtree_field": 1})

        assert listing.id == "1"
        assert listing.currency == "GBP"
        with pytest.raises(Exception, match="frozen"):
            listing.title = "other"  # type: ignore[misc]
