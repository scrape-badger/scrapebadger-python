"""Unit tests for Walmart SDK methods and models.

Tests cover:
- TestWalmartClient: sub-client wiring on WalmartClient and ScrapeBadger
- TestRouting: every one of the 11 endpoints routes to the right path/params
- TestWalmartModels: model parsing, immutability, and the deliberate
  ``total_results_reported`` / ``max_page`` naming on SearchResponse
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from scrapebadger.walmart.client import WalmartClient
from scrapebadger.walmart.models import (
    AutocompleteResponse,
    MarketsResponse,
    Product,
    ReviewsResponse,
    SearchResponse,
    SellerResponse,
    StoreResponse,
)

SEARCH_RESPONSE: dict[str, Any] = {
    "query": "laptop",
    "page": 1,
    "total_results_reported": 14713,
    "max_page": 10,
    "result_count": 1,
    "items": [
        {
            "us_item_id": "5689919121",
            "name": "HP Laptop 15",
            "price": 279.0,
            "currency": "USD",
            "position": 1,
            "badges": [{"id": "b1", "text": "Rollback", "type": "price"}],
        }
    ],
}


@pytest.fixture
def mock_base_client() -> MagicMock:
    """Return a mock BaseClient with AsyncMock methods."""
    client = MagicMock()
    client.get = AsyncMock()
    return client


@pytest.fixture
def walmart(mock_base_client: MagicMock) -> WalmartClient:
    return WalmartClient(mock_base_client)


class TestWalmartClient:
    def test_sub_clients_are_wired_and_cached(self, walmart: WalmartClient) -> None:
        assert walmart.search is walmart.search
        assert walmart.products is walmart.products
        assert walmart.sellers is walmart.sellers
        assert walmart.stores is walmart.stores
        assert walmart.reference is walmart.reference

    def test_exposed_on_main_client(self) -> None:
        from scrapebadger import ScrapeBadger

        client = ScrapeBadger(api_key="test-key")
        assert isinstance(client.walmart, WalmartClient)
        assert client.walmart is client.walmart


class TestRouting:
    async def test_search(self, walmart: WalmartClient, mock_base_client: MagicMock) -> None:
        mock_base_client.get.return_value = SEARCH_RESPONSE
        result = await walmart.search.search(
            "laptop", page=2, sort="price_low", min_price=10, max_price=500, facet="brand:HP"
        )

        assert isinstance(result, SearchResponse)
        path, kwargs = mock_base_client.get.call_args[0][0], mock_base_client.get.call_args[1]
        assert path == "/v1/walmart/search"
        assert kwargs["params"] == {
            "query": "laptop",
            "page": 2,
            "sort": "price_low",
            "min_price": 10,
            "max_price": 500,
            "facet": "brand:HP",
        }

    async def test_category_has_no_sort(
        self, walmart: WalmartClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = SEARCH_RESPONSE
        await walmart.search.category("electronics/3944", page=3)

        assert mock_base_client.get.call_args[0][0] == "/v1/walmart/category"
        params = mock_base_client.get.call_args[1]["params"]
        assert params["path"] == "electronics/3944"
        assert params["page"] == 3
        assert "sort" not in params

    async def test_deals(self, walmart: WalmartClient, mock_base_client: MagicMock) -> None:
        mock_base_client.get.return_value = SEARCH_RESPONSE
        await walmart.search.deals(page=4, max_price=50)

        assert mock_base_client.get.call_args[0][0] == "/v1/walmart/deals"
        assert mock_base_client.get.call_args[1]["params"] == {
            "page": 4,
            "min_price": None,
            "max_price": 50,
        }

    async def test_autocomplete(self, walmart: WalmartClient, mock_base_client: MagicMock) -> None:
        mock_base_client.get.return_value = {
            "query": "lapt",
            "result_count": 1,
            "suggestions": [{"query": "laptop", "type": "keyword"}],
        }
        result = await walmart.search.autocomplete("lapt")

        assert isinstance(result, AutocompleteResponse)
        assert mock_base_client.get.call_args[0][0] == "/v1/walmart/autocomplete"
        assert mock_base_client.get.call_args[1]["params"] == {"query": "lapt"}

    async def test_get_product(self, walmart: WalmartClient, mock_base_client: MagicMock) -> None:
        mock_base_client.get.return_value = {"us_item_id": "5689919121", "name": "HP Laptop 15"}
        result = await walmart.products.get_product("5689919121")

        assert isinstance(result, Product)
        assert mock_base_client.get.call_args[0][0] == "/v1/walmart/products/5689919121"

    async def test_get_reviews(self, walmart: WalmartClient, mock_base_client: MagicMock) -> None:
        mock_base_client.get.return_value = {"item_id": "5689919121", "page": 2, "result_count": 0}
        result = await walmart.products.get_reviews("5689919121", page=2, sort="rating-desc")

        assert isinstance(result, ReviewsResponse)
        assert mock_base_client.get.call_args[0][0] == "/v1/walmart/products/5689919121/reviews"
        assert mock_base_client.get.call_args[1]["params"] == {"page": 2, "sort": "rating-desc"}

    async def test_get_seller(self, walmart: WalmartClient, mock_base_client: MagicMock) -> None:
        mock_base_client.get.return_value = {"seller": {"seller_id": "101040442", "name": "ACME"}}
        result = await walmart.sellers.get_seller("101040442")

        assert isinstance(result, SellerResponse)
        assert mock_base_client.get.call_args[0][0] == "/v1/walmart/sellers/101040442"

    async def test_get_seller_products_requires_query(
        self, walmart: WalmartClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = SEARCH_RESPONSE
        await walmart.sellers.get_seller_products("101040442", "laptop", page=2)

        assert mock_base_client.get.call_args[0][0] == "/v1/walmart/sellers/101040442/products"
        assert mock_base_client.get.call_args[1]["params"] == {
            "query": "laptop",
            "page": 2,
            "sort": None,
        }

    async def test_get_store(self, walmart: WalmartClient, mock_base_client: MagicMock) -> None:
        mock_base_client.get.return_value = {"store": {"store_id": "100"}, "nearby_count": 0}
        result = await walmart.stores.get_store("100")

        assert isinstance(result, StoreResponse)
        assert mock_base_client.get.call_args[0][0] == "/v1/walmart/stores/100"

    async def test_list_markets(self, walmart: WalmartClient, mock_base_client: MagicMock) -> None:
        mock_base_client.get.return_value = {
            "result_count": 1,
            "markets": [
                {
                    "code": "US",
                    "name": "United States",
                    "domain": "walmart.com",
                    "currency": "USD",
                    "language": "en-US",
                }
            ],
        }
        result = await walmart.reference.list_markets()

        assert isinstance(result, MarketsResponse)
        assert result.markets[0].domain == "walmart.com"
        assert mock_base_client.get.call_args[0][0] == "/v1/walmart/markets"

    async def test_health(self, walmart: WalmartClient, mock_base_client: MagicMock) -> None:
        mock_base_client.get.return_value = {"status": "ok"}
        result = await walmart.reference.health()

        assert result == {"status": "ok"}
        assert mock_base_client.get.call_args[0][0] == "/v1/walmart/health"


class TestWalmartModels:
    def test_search_response_reports_unreachable_total(self) -> None:
        response = SearchResponse.model_validate(SEARCH_RESPONSE)

        # Deliberately NOT `total_results` — Walmart's claimed total is not
        # reachable; `max_page` is the real ceiling.
        assert response.total_results_reported == 14713
        assert response.max_page == 10
        assert response.items[0].badges[0].text == "Rollback"

    def test_nested_product_payload_survives_the_round_trip(self) -> None:
        """`extra="ignore"` drops undeclared fields silently — pin the nesting."""
        payload: dict[str, Any] = {
            "us_item_id": "5689919121",
            "name": "HP Laptop 15",
            "upc": "195908712345",
            "price": 279.0,
            "price_info": {
                "current_price": {"price": 279.0, "currency": "USD", "price_string": "$279.00"},
                "was_price": {"price": 399.0},
                "savings_amount": 120.0,
                "is_price_reduced": True,
                "price_range": {"min_price": 279.0, "max_price": 399.0},
            },
            "fulfillment_summary": [
                {
                    "fulfillment": "SHIPPING",
                    "delivery_date": "2026-08-11",
                    "sla": {"unitOfMeasure": "Days", "minimumValue": 2, "maximumValue": 4},
                    "is_free_for_wplus": True,
                }
            ],
            "seller": {
                "catalog_seller_id": "101040442",
                "seller_name": "Walmart.com",
                "seller_average_rating": 4.6,
            },
            "return_policy": {"returnable": True, "return_window": "90 days"},
            "specification_groups": [
                {"group_name": "General", "specifications": [{"name": "RAM", "value": "8 GB"}]}
            ],
            "rating_distribution": {"average_rating": 4.3, "five_star": 812},
            "top_reviews": [{"review_id": "r1", "rating": 5, "text": "great"}],
            "location": {"postal_code": "97124", "store_id": "3419"},
        }
        product = Product.model_validate(payload)

        assert product.upc == "195908712345"
        assert product.price_info is not None
        assert product.price_info.current_price is not None
        assert product.price_info.current_price.price_string == "$279.00"
        assert product.price_info.price_range is not None
        assert product.price_info.price_range.max_price == 399.0
        assert product.fulfillment_summary[0].sla == {
            "unitOfMeasure": "Days",
            "minimumValue": 2,
            "maximumValue": 4,
        }
        assert product.fulfillment_summary[0].is_free_for_wplus is True
        assert product.seller is not None
        assert product.seller.catalog_seller_id == "101040442"
        assert product.return_policy is not None
        assert product.return_policy.return_window == "90 days"
        assert product.specification_groups[0].specifications[0].value == "8 GB"
        assert product.rating_distribution is not None
        assert product.rating_distribution.five_star == 812
        assert product.top_reviews[0].rating == 5
        assert product.location is not None
        assert product.location.store_id == "3419"

        # Every key supplied must come back out — a silently dropped field is
        # the whole failure mode `extra="ignore"` hides.
        dumped = product.model_dump(exclude_none=True)
        assert set(payload) <= set(dumped)

    def test_models_are_frozen_and_ignore_unknown_fields(self) -> None:
        product = Product.model_validate({"name": "HP Laptop 15", "a_new_walmart_field": 1})

        assert product.name == "HP Laptop 15"
        with pytest.raises(Exception, match="frozen"):
            product.name = "other"  # type: ignore[misc]
