"""Unit tests for Leboncoin SDK methods and models.

Tests cover:
- TestLeboncoinModels: Pydantic model construction, validation, immutability
- TestLeboncoinClient: LeboncoinClient sub-client wiring
- TestSearchClient / TestAdsClient / TestSellersClient / TestReferenceClient:
  endpoint routing via a mocked HTTP client
- TestLeboncoinImports: public API importability
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from scrapebadger.leboncoin.ads import AdsClient
from scrapebadger.leboncoin.client import LeboncoinClient
from scrapebadger.leboncoin.models import (
    Ad,
    AdResponse,
    CategoriesResponse,
    DepartmentsResponse,
    LocationSearchResponse,
    MarketsResponse,
    RegionsResponse,
    SearchResponse,
    Seller,
    SellerListingsResponse,
    SellerResponse,
    SimilarResponse,
)
from scrapebadger.leboncoin.reference import ReferenceClient
from scrapebadger.leboncoin.search import SearchClient
from scrapebadger.leboncoin.sellers import SellersClient

# ---------------------------------------------------------------------------
# Shared sample data
# ---------------------------------------------------------------------------

SAMPLE_AD: dict[str, Any] = {
    "list_id": 2812345678,
    "subject": "Velo de course",
    "body": "Bon etat",
    "ad_type": "offer",
    "url": "https://www.leboncoin.fr/ad/2812345678",
    "category_id": "22",
    "category_name": "Velos",
    "price": [250],
    "price_cents": 25000,
    "price_eur": 250.0,
    "currency": "EUR",
    "first_publication_date": "2026-06-01 12:00:00",
    "first_publication_at": "2026-06-01T12:00:00Z",
    "has_phone": True,
    "images": {
        "nb_images": 2,
        "thumb_url": "https://img.leboncoin.fr/thumb.jpg",
        "urls": ["https://img.leboncoin.fr/1.jpg", "https://img.leboncoin.fr/2.jpg"],
    },
    "attributes": [{"key": "brand", "key_label": "Marque", "value": "Btwin"}],
    "location": {"region_id": "12", "region_name": "Nouvelle-Aquitaine", "city": "Bordeaux"},
    "owner": {"user_id": "12345678", "type": "private", "name": "Jean"},
}

SAMPLE_SELLER: dict[str, Any] = {
    "user_id": "12345678",
    "name": "Jean Dupont",
    "account_type": "private",
    "registered_at": "2020-01-01T00:00:00Z",
    "total_ads": 42,
    "location": {"region_id": "12", "city": "Bordeaux"},
    "feedback": {"overall_score": 4.8, "received_count": 30},
}

SEARCH_RESPONSE: dict[str, Any] = {
    "ads": [SAMPLE_AD],
    "total": 100,
    "total_all": 120,
    "total_pro": 20,
    "total_private": 100,
    "total_shippable": 50,
    "max_pages": 3,
    "page": 1,
    "limit": 35,
    "source": "api",
}

AD_RESPONSE: dict[str, Any] = {"ad": SAMPLE_AD}

SIMILAR_RESPONSE: dict[str, Any] = {"list_id": 2812345678, "ads": [SAMPLE_AD]}

SELLER_RESPONSE: dict[str, Any] = {"seller": SAMPLE_SELLER}

SELLER_LISTINGS_RESPONSE: dict[str, Any] = {
    "user_id": "12345678",
    "ads": [SAMPLE_AD],
    "total": 42,
    "page": 1,
    "limit": 35,
}

CATEGORIES_RESPONSE: dict[str, Any] = {
    "categories": [{"category_id": "22", "key": "velos", "label": "Velos", "parent_id": "2"}]
}

REGIONS_RESPONSE: dict[str, Any] = {
    "regions": [{"region_id": "12", "key": "nouvelle_aquitaine", "name": "Nouvelle-Aquitaine"}]
}

DEPARTMENTS_RESPONSE: dict[str, Any] = {
    "departments": [{"department_id": "33", "region_id": "12", "name": "Gironde"}]
}

LOCATION_SEARCH_RESPONSE: dict[str, Any] = {
    "query": "bordeaux",
    "suggestions": [
        {"label": "Bordeaux 33000", "location_type": "city", "city": "Bordeaux", "zipcode": "33000"}
    ],
}

MARKETS_RESPONSE: dict[str, Any] = {"markets": [{"code": "fr", "name": "Leboncoin France"}]}


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
def leboncoin_client(mock_base_client: MagicMock) -> LeboncoinClient:
    return LeboncoinClient(mock_base_client)


@pytest.fixture
def search_client(mock_base_client: MagicMock) -> SearchClient:
    return SearchClient(mock_base_client)


@pytest.fixture
def ads_client(mock_base_client: MagicMock) -> AdsClient:
    return AdsClient(mock_base_client)


@pytest.fixture
def sellers_client(mock_base_client: MagicMock) -> SellersClient:
    return SellersClient(mock_base_client)


@pytest.fixture
def reference_client(mock_base_client: MagicMock) -> ReferenceClient:
    return ReferenceClient(mock_base_client)


# ===========================================================================
# TestLeboncoinModels
# ===========================================================================


class TestLeboncoinModels:
    """Pydantic model construction, validation, and immutability tests."""

    def test_ad_full(self) -> None:
        ad = Ad.model_validate(SAMPLE_AD)
        assert ad.list_id == 2812345678
        assert ad.subject == "Velo de course"
        assert ad.price == [250]
        assert ad.price_eur == 250.0
        assert ad.images.nb_images == 2
        assert len(ad.attributes) == 1
        assert ad.attributes[0].key == "brand"
        assert ad.location.city == "Bordeaux"
        assert ad.owner.user_id == "12345678"

    def test_ad_minimal(self) -> None:
        ad = Ad(list_id=1)
        assert ad.subject == ""
        assert ad.price == []
        assert ad.currency == "EUR"
        assert ad.images.nb_images == 0
        assert ad.attributes == []
        assert ad.options == {}

    def test_ad_is_frozen(self) -> None:
        ad = Ad.model_validate(SAMPLE_AD)
        with pytest.raises(Exception):  # noqa: B017
            ad.subject = "mutated"  # type: ignore[misc]

    def test_seller_full(self) -> None:
        seller = Seller.model_validate(SAMPLE_SELLER)
        assert seller.user_id == "12345678"
        assert seller.account_type == "private"
        assert seller.total_ads == 42
        assert seller.feedback is not None
        assert seller.feedback.overall_score == 4.8

    # -- Response envelopes --

    def test_search_response(self) -> None:
        resp = SearchResponse.model_validate(SEARCH_RESPONSE)
        assert len(resp.ads) == 1
        assert resp.total == 100
        assert resp.total_pro == 20
        assert resp.max_pages == 3
        assert resp.source == "api"

    def test_search_response_defaults(self) -> None:
        resp = SearchResponse.model_validate({})
        assert resp.ads == []
        assert resp.page == 1
        assert resp.limit == 35
        assert resp.source == "api"

    def test_ad_response(self) -> None:
        resp = AdResponse.model_validate(AD_RESPONSE)
        assert resp.ad.list_id == 2812345678

    def test_similar_response(self) -> None:
        resp = SimilarResponse.model_validate(SIMILAR_RESPONSE)
        assert resp.list_id == 2812345678
        assert len(resp.ads) == 1

    def test_seller_response(self) -> None:
        resp = SellerResponse.model_validate(SELLER_RESPONSE)
        assert resp.seller.user_id == "12345678"

    def test_seller_listings_response(self) -> None:
        resp = SellerListingsResponse.model_validate(SELLER_LISTINGS_RESPONSE)
        assert resp.user_id == "12345678"
        assert len(resp.ads) == 1
        assert resp.total == 42

    def test_categories_response(self) -> None:
        resp = CategoriesResponse.model_validate(CATEGORIES_RESPONSE)
        assert len(resp.categories) == 1
        assert resp.categories[0].category_id == "22"

    def test_regions_response(self) -> None:
        resp = RegionsResponse.model_validate(REGIONS_RESPONSE)
        assert len(resp.regions) == 1
        assert resp.regions[0].name == "Nouvelle-Aquitaine"

    def test_departments_response(self) -> None:
        resp = DepartmentsResponse.model_validate(DEPARTMENTS_RESPONSE)
        assert len(resp.departments) == 1
        assert resp.departments[0].department_id == "33"

    def test_location_search_response(self) -> None:
        resp = LocationSearchResponse.model_validate(LOCATION_SEARCH_RESPONSE)
        assert resp.query == "bordeaux"
        assert len(resp.suggestions) == 1
        assert resp.suggestions[0].zipcode == "33000"

    def test_markets_response(self) -> None:
        resp = MarketsResponse.model_validate(MARKETS_RESPONSE)
        assert len(resp.markets) == 1
        assert resp.markets[0]["code"] == "fr"

    def test_ignores_unknown_fields(self) -> None:
        resp = SearchResponse.model_validate({"ads": [], "unexpected": 123})
        assert resp.ads == []


# ===========================================================================
# TestLeboncoinClient
# ===========================================================================


class TestLeboncoinClient:
    """Tests for LeboncoinClient sub-client wiring."""

    def test_search_property(self, leboncoin_client: LeboncoinClient) -> None:
        assert isinstance(leboncoin_client.search, SearchClient)

    def test_ads_property(self, leboncoin_client: LeboncoinClient) -> None:
        assert isinstance(leboncoin_client.ads, AdsClient)

    def test_sellers_property(self, leboncoin_client: LeboncoinClient) -> None:
        assert isinstance(leboncoin_client.sellers, SellersClient)

    def test_reference_property(self, leboncoin_client: LeboncoinClient) -> None:
        assert isinstance(leboncoin_client.reference, ReferenceClient)

    def test_sub_clients_are_stable(self, leboncoin_client: LeboncoinClient) -> None:
        assert leboncoin_client.search is leboncoin_client.search
        assert leboncoin_client.ads is leboncoin_client.ads
        assert leboncoin_client.sellers is leboncoin_client.sellers
        assert leboncoin_client.reference is leboncoin_client.reference


# ===========================================================================
# TestSearchClient
# ===========================================================================


class TestSearchClient:
    async def test_search_default_params(
        self, search_client: SearchClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = SEARCH_RESPONSE
        result = await search_client.search("velo")

        assert isinstance(result, SearchResponse)
        call_args = mock_base_client.get.call_args
        assert call_args[0][0] == "/v1/leboncoin/search"
        params = call_args[1]["params"]
        assert params["text"] == "velo"
        assert params["page"] == 1
        assert params["sort"] is None
        assert params["owner_type"] is None

    async def test_search_with_filters(
        self, search_client: SearchClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = SEARCH_RESPONSE
        await search_client.search(
            "velo",
            category="22",
            region_id="12",
            department_id="33",
            city="Bordeaux",
            zipcode="33000",
            price_min=100,
            price_max=500,
            owner_type="private",
            ad_type="offer",
            sort="price_low",
            page=2,
            limit=50,
        )
        params = mock_base_client.get.call_args[1]["params"]
        assert params["category"] == "22"
        assert params["region_id"] == "12"
        assert params["department_id"] == "33"
        assert params["city"] == "Bordeaux"
        assert params["zipcode"] == "33000"
        assert params["price_min"] == 100
        assert params["price_max"] == 500
        assert params["owner_type"] == "private"
        assert params["ad_type"] == "offer"
        assert params["sort"] == "price_low"
        assert params["page"] == 2
        assert params["limit"] == 50


# ===========================================================================
# TestAdsClient
# ===========================================================================


class TestAdsClient:
    async def test_get_ad(self, ads_client: AdsClient, mock_base_client: MagicMock) -> None:
        mock_base_client.get.return_value = AD_RESPONSE
        result = await ads_client.get_ad(2812345678)
        assert isinstance(result, AdResponse)
        assert result.ad.list_id == 2812345678
        assert mock_base_client.get.call_args[0][0] == "/v1/leboncoin/ads/2812345678"

    async def test_get_similar(self, ads_client: AdsClient, mock_base_client: MagicMock) -> None:
        mock_base_client.get.return_value = SIMILAR_RESPONSE
        result = await ads_client.get_similar(2812345678, limit=10)
        assert isinstance(result, SimilarResponse)
        call_args = mock_base_client.get.call_args
        assert call_args[0][0] == "/v1/leboncoin/ads/2812345678/similar"
        assert call_args[1]["params"]["limit"] == 10


# ===========================================================================
# TestSellersClient
# ===========================================================================


class TestSellersClient:
    async def test_get_seller(
        self, sellers_client: SellersClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = SELLER_RESPONSE
        result = await sellers_client.get_seller("12345678")
        assert isinstance(result, SellerResponse)
        assert mock_base_client.get.call_args[0][0] == "/v1/leboncoin/sellers/12345678"

    async def test_get_seller_listings(
        self, sellers_client: SellersClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = SELLER_LISTINGS_RESPONSE
        result = await sellers_client.get_seller_listings("12345678", page=2, limit=50)
        assert isinstance(result, SellerListingsResponse)
        call_args = mock_base_client.get.call_args
        assert call_args[0][0] == "/v1/leboncoin/sellers/12345678/listings"
        assert call_args[1]["params"]["page"] == 2
        assert call_args[1]["params"]["limit"] == 50


# ===========================================================================
# TestReferenceClient
# ===========================================================================


class TestReferenceClient:
    async def test_list_categories(
        self, reference_client: ReferenceClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = CATEGORIES_RESPONSE
        result = await reference_client.list_categories()
        assert isinstance(result, CategoriesResponse)
        mock_base_client.get.assert_called_once_with("/v1/leboncoin/categories")

    async def test_list_regions(
        self, reference_client: ReferenceClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = REGIONS_RESPONSE
        result = await reference_client.list_regions()
        assert isinstance(result, RegionsResponse)
        mock_base_client.get.assert_called_once_with("/v1/leboncoin/regions")

    async def test_list_departments(
        self, reference_client: ReferenceClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = DEPARTMENTS_RESPONSE
        result = await reference_client.list_departments(region_id="12")
        assert isinstance(result, DepartmentsResponse)
        call_args = mock_base_client.get.call_args
        assert call_args[0][0] == "/v1/leboncoin/departments"
        assert call_args[1]["params"]["region_id"] == "12"

    async def test_search_locations(
        self, reference_client: ReferenceClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = LOCATION_SEARCH_RESPONSE
        result = await reference_client.search_locations("bordeaux")
        assert isinstance(result, LocationSearchResponse)
        call_args = mock_base_client.get.call_args
        assert call_args[0][0] == "/v1/leboncoin/locations/search"
        assert call_args[1]["params"]["q"] == "bordeaux"

    async def test_list_markets(
        self, reference_client: ReferenceClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = MARKETS_RESPONSE
        result = await reference_client.list_markets()
        assert isinstance(result, MarketsResponse)
        mock_base_client.get.assert_called_once_with("/v1/leboncoin/markets")


# ===========================================================================
# TestLeboncoinImports
# ===========================================================================


class TestLeboncoinImports:
    def test_leboncoin_client_importable(self) -> None:
        from scrapebadger.leboncoin import LeboncoinClient as _  # noqa: F401

    def test_leboncoin_client_top_level_importable(self) -> None:
        from scrapebadger import LeboncoinClient as _  # noqa: F401

    def test_leboncoin_ad_top_level_importable(self) -> None:
        from scrapebadger import LeboncoinAd as _  # noqa: F401

    def test_search_response_importable(self) -> None:
        from scrapebadger.leboncoin import SearchResponse as _  # noqa: F401

    def test_leboncoin_seller_top_level_importable(self) -> None:
        from scrapebadger import LeboncoinSeller as _  # noqa: F401
