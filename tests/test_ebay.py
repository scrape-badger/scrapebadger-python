"""Unit tests for eBay SDK methods and models.

Tests cover:
- TestEbayModels: Pydantic model construction, validation, immutability
- TestEbayClient: EbayClient sub-client wiring
- TestSearchClient / TestItemsClient / TestSellersClient / TestCategoriesClient /
  TestReferenceClient: endpoint routing via a mocked HTTP client
- TestEbayImports: public API importability
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from scrapebadger.ebay.categories import CategoriesClient
from scrapebadger.ebay.client import EbayClient
from scrapebadger.ebay.items import ItemsClient
from scrapebadger.ebay.models import (
    AutocompleteResponse,
    CategoriesResponse,
    CategoryResponse,
    EbayPrice,
    Item,
    ItemDetailResponse,
    MarketsResponse,
    RatingHistogram,
    Review,
    ReviewsResponse,
    SearchResponse,
    SearchResult,
    Seller,
    SellerFeedbackResponse,
    SellerItemsResponse,
    SellerProfileResponse,
)
from scrapebadger.ebay.reference import ReferenceClient
from scrapebadger.ebay.search import SearchClient
from scrapebadger.ebay.sellers import SellersClient

# ---------------------------------------------------------------------------
# Shared sample data
# ---------------------------------------------------------------------------

SAMPLE_PRICE: dict[str, Any] = {
    "value": 29.99,
    "currency": "USD",
    "symbol": "$",
    "raw": "$29.99",
}

SAMPLE_SEARCH_RESULT: dict[str, Any] = {
    "position": 1,
    "item_id": "123456789012",
    "product_id": "987654321",
    "title": "Nintendo Switch OLED",
    "url": "https://www.ebay.com/itm/123456789012",
    "image": "https://i.ebayimg.com/abc.jpg",
    "price": SAMPLE_PRICE,
    "original_price": {"value": 49.99, "currency": "USD", "symbol": "$", "raw": "$49.99"},
    "discount_percent": 40.0,
    "condition": "New",
    "brand": "Nintendo",
    "buying_format": "Buy It Now",
    "is_auction": False,
    "bids": None,
    "free_shipping": True,
    "location": "United States",
    "sold_count": 1200,
    "watchers": 42,
    "rating": 4.8,
    "ratings_total": 530,
    "seller_name": "musicmagpie",
    "seller_feedback_percent": 99.4,
    "seller_feedback_score": 100000,
    "is_sponsored": False,
}

SAMPLE_ITEM: dict[str, Any] = {
    "item_id": "123456789012",
    "product_id": "987654321",
    "legacy_item_id": "111222333",
    "title": "Nintendo Switch OLED",
    "subtitle": "White Joy-Con",
    "url": "https://www.ebay.com/itm/123456789012",
    "condition": "New",
    "condition_id": "1000",
    "price": SAMPLE_PRICE,
    "currency": "USD",
    "availability": "In stock",
    "quantity_available": 10,
    "quantity_sold": 1200,
    "watchers": 42,
    "buying_format": "Buy It Now",
    "is_auction": False,
    "best_offer_enabled": True,
    "brand": "Nintendo",
    "mpn": "HEGSKAAAA",
    "model": "OLED",
    "gtin": "0045496453435",
    "main_image": "https://i.ebayimg.com/abc.jpg",
    "images": [{"url": "https://i.ebayimg.com/abc.jpg", "width": 500, "height": 500}],
    "images_count": 1,
    "description": "Brand new sealed.",
    "item_specifics": {"Brand": "Nintendo", "Model": "OLED"},
    "categories": ["Video Games & Consoles", "Video Game Consoles"],
    "category_id": "139971",
    "shipping_options": [
        {
            "cost": {"value": 0.0, "currency": "USD", "symbol": "$", "raw": "Free"},
            "is_free": True,
            "service": "Standard Shipping",
            "destination_country": "US",
        }
    ],
    "free_shipping": True,
    "item_location": "California, United States",
    "ships_to": ["United States", "Canada"],
    "returns": {"accepted": True, "period": "30 days", "cost_paid_by": "seller", "raw": "30 days"},
    "seller": {
        "username": "musicmagpie",
        "url": "https://www.ebay.com/usr/musicmagpie",
        "feedback_score": 100000,
        "feedback_percent": 99.4,
        "store_name": "musicMagpie Store",
    },
    "rating": 4.8,
    "ratings_total": 530,
    "date_modified_utc": 1751500000.0,
    "date_modified_at": "2026-06-03T00:00:00Z",
    "scraped_utc": 1751500000.0,
    "scraped_at": "2026-06-03T00:00:00Z",
}

SAMPLE_REVIEW: dict[str, Any] = {
    "title": "Great console",
    "body": "Works perfectly.",
    "rating": 5.0,
    "author": "gamer42",
    "date_raw": "June 1, 2026",
    "date_utc": 1751328000.0,
    "date_at": "2026-06-01T00:00:00Z",
    "helpful_votes": 12,
    "verified_purchase": True,
}

SAMPLE_SELLER: dict[str, Any] = {
    "username": "musicmagpie",
    "url": "https://www.ebay.com/usr/musicmagpie",
    "store_name": "musicMagpie Store",
    "store_url": "https://www.ebay.com/str/musicmagpie",
    "feedback_score": 100000,
    "feedback_percent": 99.4,
    "member_since": "Jan 1, 2010",
    "location": "United Kingdom",
    "items_for_sale": 50000,
    "feedback_12mo": {"positive": 96000, "neutral": 2000, "negative": 2000},
    "top_rated": True,
    "scraped_utc": 1751500000.0,
    "scraped_at": "2026-06-03T00:00:00Z",
}

SAMPLE_FEEDBACK_ENTRY: dict[str, Any] = {
    "rating": "positive",
    "comment": "Fast shipping",
    "rater": "buyer123",
    "item": "Nintendo Switch OLED",
    "date_raw": "June 1, 2026",
    "date_utc": 1751328000.0,
    "date_at": "2026-06-01T00:00:00Z",
}

SAMPLE_MARKET: dict[str, Any] = {
    "code": "US",
    "domain": "com",
    "country": "United States",
    "currency": "USD",
    "locale": "en-US",
    "name": "eBay US",
    "site_id": 0,
}

SAMPLE_CATEGORY: dict[str, Any] = {
    "name": "Video Games & Consoles",
    "category_id": "1249",
    "parent": None,
}

SAMPLE_PAGINATION: dict[str, Any] = {
    "current_page": 1,
    "per_page": 60,
    "total_pages": 20,
    "total_results": 1200,
}

SEARCH_RESPONSE: dict[str, Any] = {
    "query": "nintendo switch",
    "domain": "com",
    "results": [SAMPLE_SEARCH_RESULT],
    "facets": {"condition": ["New", "Used"]},
    "pagination": SAMPLE_PAGINATION,
    "scraped_utc": 1751500000.0,
    "scraped_at": "2026-06-03T00:00:00Z",
}

COMPLETED_RESPONSE: dict[str, Any] = {
    "query": "nintendo switch",
    "domain": "com",
    "sold": True,
    "results": [SAMPLE_SEARCH_RESULT],
    "pagination": SAMPLE_PAGINATION,
}

ITEM_DETAIL_RESPONSE: dict[str, Any] = {"domain": "com", "item": SAMPLE_ITEM}

REVIEWS_RESPONSE: dict[str, Any] = {
    "domain": "com",
    "item_id": "123456789012",
    "product_id": "987654321",
    "rating": 4.8,
    "ratings_total": 530,
    "histogram": {
        "five_star": 400,
        "four_star": 80,
        "three_star": 30,
        "two_star": 10,
        "one_star": 10,
    },
    "reviews": [SAMPLE_REVIEW],
    "pagination": SAMPLE_PAGINATION,
}

SELLER_PROFILE_RESPONSE: dict[str, Any] = {"domain": "com", "seller": SAMPLE_SELLER}

SELLER_ITEMS_RESPONSE: dict[str, Any] = {
    "domain": "com",
    "username": "musicmagpie",
    "results": [SAMPLE_SEARCH_RESULT],
    "pagination": SAMPLE_PAGINATION,
}

SELLER_FEEDBACK_RESPONSE: dict[str, Any] = {
    "domain": "com",
    "username": "musicmagpie",
    "feedback": [SAMPLE_FEEDBACK_ENTRY],
    "pagination": SAMPLE_PAGINATION,
}

CATEGORY_RESPONSE: dict[str, Any] = {
    "domain": "com",
    "category_id": "139971",
    "results": [SAMPLE_SEARCH_RESULT],
    "pagination": SAMPLE_PAGINATION,
}

AUTOCOMPLETE_RESPONSE: dict[str, Any] = {
    "query": "nint",
    "domain": "com",
    "suggestions": [{"value": "nintendo switch"}, {"value": "nintendo switch oled"}],
}

MARKETS_RESPONSE: dict[str, Any] = {"markets": [SAMPLE_MARKET]}

CATEGORIES_RESPONSE: dict[str, Any] = {"categories": [SAMPLE_CATEGORY]}


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
def ebay_client(mock_base_client: MagicMock) -> EbayClient:
    return EbayClient(mock_base_client)


@pytest.fixture
def search_client(mock_base_client: MagicMock) -> SearchClient:
    return SearchClient(mock_base_client)


@pytest.fixture
def items_client(mock_base_client: MagicMock) -> ItemsClient:
    return ItemsClient(mock_base_client)


@pytest.fixture
def sellers_client(mock_base_client: MagicMock) -> SellersClient:
    return SellersClient(mock_base_client)


@pytest.fixture
def categories_client(mock_base_client: MagicMock) -> CategoriesClient:
    return CategoriesClient(mock_base_client)


@pytest.fixture
def reference_client(mock_base_client: MagicMock) -> ReferenceClient:
    return ReferenceClient(mock_base_client)


# ===========================================================================
# TestEbayModels
# ===========================================================================


class TestEbayModels:
    """Pydantic model construction, validation, and immutability tests."""

    def test_ebay_price(self) -> None:
        price = EbayPrice.model_validate(SAMPLE_PRICE)
        assert price.value == 29.99
        assert price.currency == "USD"
        assert price.symbol == "$"
        assert price.raw == "$29.99"

    def test_ebay_price_defaults(self) -> None:
        price = EbayPrice()
        assert price.value is None
        assert price.currency is None

    def test_ebay_price_is_frozen(self) -> None:
        price = EbayPrice.model_validate(SAMPLE_PRICE)
        with pytest.raises(Exception):  # noqa: B017
            price.value = 1.0  # type: ignore[misc]

    def test_search_result(self) -> None:
        result = SearchResult.model_validate(SAMPLE_SEARCH_RESULT)
        assert result.position == 1
        assert result.item_id == "123456789012"
        assert result.price is not None
        assert result.price.value == 29.99
        assert result.free_shipping is True
        assert result.seller_name == "musicmagpie"

    def test_search_result_minimal(self) -> None:
        result = SearchResult(position=1, item_id="X")
        assert result.title is None
        assert result.is_auction is False
        assert result.is_sponsored is False
        assert result.price is None

    def test_item_full(self) -> None:
        item = Item.model_validate(SAMPLE_ITEM)
        assert item.item_id == "123456789012"
        assert item.product_id == "987654321"
        assert item.legacy_item_id == "111222333"
        assert item.best_offer_enabled is True
        assert len(item.images) == 1
        assert item.images[0].width == 500
        assert item.item_specifics == {"Brand": "Nintendo", "Model": "OLED"}
        assert item.categories == ["Video Games & Consoles", "Video Game Consoles"]
        assert len(item.shipping_options) == 1
        assert item.shipping_options[0].is_free is True
        assert item.returns is not None
        assert item.returns.accepted is True
        assert item.seller is not None
        assert item.seller.username == "musicmagpie"
        assert item.scraped_utc == 1751500000.0

    def test_item_minimal(self) -> None:
        item = Item(item_id="X")
        assert item.title is None
        assert item.images == []
        assert item.images_count == 0
        assert item.item_specifics == {}
        assert item.is_auction is False

    def test_item_is_frozen(self) -> None:
        item = Item.model_validate(SAMPLE_ITEM)
        with pytest.raises(Exception):  # noqa: B017
            item.title = "mutated"  # type: ignore[misc]

    def test_rating_histogram(self) -> None:
        hist = RatingHistogram.model_validate(REVIEWS_RESPONSE["histogram"])
        assert hist.five_star == 400
        assert hist.one_star == 10

    def test_review_full(self) -> None:
        review = Review.model_validate(SAMPLE_REVIEW)
        assert review.rating == 5.0
        assert review.author == "gamer42"
        assert review.date_utc == 1751328000.0
        assert review.verified_purchase is True

    def test_seller_full(self) -> None:
        seller = Seller.model_validate(SAMPLE_SELLER)
        assert seller.username == "musicmagpie"
        assert seller.feedback_score == 100000
        assert seller.feedback_12mo is not None
        assert seller.feedback_12mo.positive == 96000
        assert seller.top_rated is True

    # -- Response envelopes --

    def test_search_response(self) -> None:
        resp = SearchResponse.model_validate(SEARCH_RESPONSE)
        assert resp.query == "nintendo switch"
        assert resp.domain == "com"
        assert len(resp.results) == 1
        assert resp.facets == {"condition": ["New", "Used"]}
        assert resp.pagination.current_page == 1
        assert resp.scraped_utc == 1751500000.0

    def test_search_response_defaults(self) -> None:
        resp = SearchResponse.model_validate({"domain": "com"})
        assert resp.results == []
        assert resp.facets == {}
        assert resp.pagination.current_page == 1
        assert resp.sold is False

    def test_completed_response(self) -> None:
        resp = SearchResponse.model_validate(COMPLETED_RESPONSE)
        assert resp.sold is True
        assert len(resp.results) == 1

    def test_item_detail_response(self) -> None:
        resp = ItemDetailResponse.model_validate(ITEM_DETAIL_RESPONSE)
        assert resp.domain == "com"
        assert resp.item.item_id == "123456789012"

    def test_reviews_response(self) -> None:
        resp = ReviewsResponse.model_validate(REVIEWS_RESPONSE)
        assert resp.item_id == "123456789012"
        assert resp.product_id == "987654321"
        assert len(resp.reviews) == 1
        assert resp.rating == 4.8
        assert resp.histogram is not None
        assert resp.histogram.five_star == 400

    def test_seller_profile_response(self) -> None:
        resp = SellerProfileResponse.model_validate(SELLER_PROFILE_RESPONSE)
        assert resp.seller.username == "musicmagpie"

    def test_seller_items_response(self) -> None:
        resp = SellerItemsResponse.model_validate(SELLER_ITEMS_RESPONSE)
        assert resp.username == "musicmagpie"
        assert len(resp.results) == 1

    def test_seller_feedback_response(self) -> None:
        resp = SellerFeedbackResponse.model_validate(SELLER_FEEDBACK_RESPONSE)
        assert resp.username == "musicmagpie"
        assert len(resp.feedback) == 1
        assert resp.feedback[0].rating == "positive"

    def test_category_response(self) -> None:
        resp = CategoryResponse.model_validate(CATEGORY_RESPONSE)
        assert resp.category_id == "139971"
        assert len(resp.results) == 1

    def test_autocomplete_response(self) -> None:
        resp = AutocompleteResponse.model_validate(AUTOCOMPLETE_RESPONSE)
        assert resp.query == "nint"
        assert len(resp.suggestions) == 2
        assert resp.suggestions[0].value == "nintendo switch"

    def test_markets_response(self) -> None:
        resp = MarketsResponse.model_validate(MARKETS_RESPONSE)
        assert len(resp.markets) == 1
        assert resp.markets[0].code == "US"
        assert resp.markets[0].site_id == 0

    def test_categories_response(self) -> None:
        resp = CategoriesResponse.model_validate(CATEGORIES_RESPONSE)
        assert len(resp.categories) == 1
        assert resp.categories[0].category_id == "1249"

    def test_ignores_unknown_fields(self) -> None:
        resp = MarketsResponse.model_validate({"markets": [], "unexpected": 123})
        assert resp.markets == []


# ===========================================================================
# TestEbayClient
# ===========================================================================


class TestEbayClient:
    """Tests for EbayClient sub-client wiring."""

    def test_search_property(self, ebay_client: EbayClient) -> None:
        assert isinstance(ebay_client.search, SearchClient)

    def test_items_property(self, ebay_client: EbayClient) -> None:
        assert isinstance(ebay_client.items, ItemsClient)

    def test_sellers_property(self, ebay_client: EbayClient) -> None:
        assert isinstance(ebay_client.sellers, SellersClient)

    def test_categories_property(self, ebay_client: EbayClient) -> None:
        assert isinstance(ebay_client.categories, CategoriesClient)

    def test_reference_property(self, ebay_client: EbayClient) -> None:
        assert isinstance(ebay_client.reference, ReferenceClient)

    def test_sub_clients_are_stable(self, ebay_client: EbayClient) -> None:
        assert ebay_client.search is ebay_client.search
        assert ebay_client.items is ebay_client.items
        assert ebay_client.sellers is ebay_client.sellers
        assert ebay_client.categories is ebay_client.categories
        assert ebay_client.reference is ebay_client.reference


# ===========================================================================
# TestSearchClient
# ===========================================================================


class TestSearchClient:
    async def test_search_default_params(
        self, search_client: SearchClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = SEARCH_RESPONSE
        result = await search_client.search("nintendo switch")

        assert isinstance(result, SearchResponse)
        call_args = mock_base_client.get.call_args
        assert call_args[0][0] == "/v1/ebay/search"
        params = call_args[1]["params"]
        assert params["query"] == "nintendo switch"
        assert params["domain"] == "com"
        assert params["page"] == 1
        assert params["sort_by"] is None
        assert params["buying_format"] is None

    async def test_search_with_filters(
        self, search_client: SearchClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = SEARCH_RESPONSE
        await search_client.search(
            "laptop",
            domain="de",
            category_id="177",
            page=2,
            per_page=120,
            sort_by="price_low_to_high",
            condition="used",
            buying_format="auction",
            min_price=100,
            max_price=500,
            free_shipping=True,
        )
        params = mock_base_client.get.call_args[1]["params"]
        assert params["domain"] == "de"
        assert params["category_id"] == "177"
        assert params["page"] == 2
        assert params["per_page"] == 120
        assert params["sort_by"] == "price_low_to_high"
        assert params["condition"] == "used"
        assert params["buying_format"] == "auction"
        assert params["min_price"] == 100
        assert params["max_price"] == 500
        assert params["free_shipping"] is True

    async def test_completed(
        self, search_client: SearchClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = COMPLETED_RESPONSE
        result = await search_client.completed("iphone 13", condition="used")
        assert isinstance(result, SearchResponse)
        assert result.sold is True
        call_args = mock_base_client.get.call_args
        assert call_args[0][0] == "/v1/ebay/completed"
        assert call_args[1]["params"]["condition"] == "used"

    async def test_autocomplete(
        self, search_client: SearchClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = AUTOCOMPLETE_RESPONSE
        result = await search_client.autocomplete("nint", domain="co.uk")
        assert isinstance(result, AutocompleteResponse)
        call_args = mock_base_client.get.call_args
        assert call_args[0][0] == "/v1/ebay/autocomplete"
        assert call_args[1]["params"]["query"] == "nint"
        assert call_args[1]["params"]["domain"] == "co.uk"


# ===========================================================================
# TestItemsClient
# ===========================================================================


class TestItemsClient:
    async def test_get_item(self, items_client: ItemsClient, mock_base_client: MagicMock) -> None:
        mock_base_client.get.return_value = ITEM_DETAIL_RESPONSE
        result = await items_client.get_item("123456789012", domain="de")
        assert isinstance(result, ItemDetailResponse)
        assert result.item.item_id == "123456789012"
        call_args = mock_base_client.get.call_args
        assert call_args[0][0] == "/v1/ebay/items/123456789012"
        assert call_args[1]["params"]["domain"] == "de"

    async def test_get_item_reviews(
        self, items_client: ItemsClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = REVIEWS_RESPONSE
        result = await items_client.get_item_reviews("123456789012", page=2)
        assert isinstance(result, ReviewsResponse)
        call_args = mock_base_client.get.call_args
        assert call_args[0][0] == "/v1/ebay/items/123456789012/reviews"
        params = call_args[1]["params"]
        assert params["page"] == 2
        assert params["product_id"] is None

    async def test_get_item_reviews_with_product_id(
        self, items_client: ItemsClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = REVIEWS_RESPONSE
        await items_client.get_item_reviews("123456789012", product_id="987654321")
        params = mock_base_client.get.call_args[1]["params"]
        assert params["product_id"] == "987654321"


# ===========================================================================
# TestSellersClient
# ===========================================================================


class TestSellersClient:
    async def test_get_seller(
        self, sellers_client: SellersClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = SELLER_PROFILE_RESPONSE
        result = await sellers_client.get_seller("musicmagpie")
        assert isinstance(result, SellerProfileResponse)
        assert mock_base_client.get.call_args[0][0] == "/v1/ebay/sellers/musicmagpie"

    async def test_get_seller_items(
        self, sellers_client: SellersClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = SELLER_ITEMS_RESPONSE
        result = await sellers_client.get_seller_items("musicmagpie", query="switch", page=3)
        assert isinstance(result, SellerItemsResponse)
        call_args = mock_base_client.get.call_args
        assert call_args[0][0] == "/v1/ebay/sellers/musicmagpie/items"
        assert call_args[1]["params"]["query"] == "switch"
        assert call_args[1]["params"]["page"] == 3

    async def test_get_seller_feedback(
        self, sellers_client: SellersClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = SELLER_FEEDBACK_RESPONSE
        result = await sellers_client.get_seller_feedback("musicmagpie")
        assert isinstance(result, SellerFeedbackResponse)
        assert mock_base_client.get.call_args[0][0] == "/v1/ebay/sellers/musicmagpie/feedback"


# ===========================================================================
# TestCategoriesClient
# ===========================================================================


class TestCategoriesClient:
    async def test_browse_category(
        self, categories_client: CategoriesClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = CATEGORY_RESPONSE
        result = await categories_client.browse_category(
            "139971", sort_by="newly_listed", min_price=10
        )
        assert isinstance(result, CategoryResponse)
        call_args = mock_base_client.get.call_args
        assert call_args[0][0] == "/v1/ebay/categories/139971/items"
        assert call_args[1]["params"]["sort_by"] == "newly_listed"
        assert call_args[1]["params"]["min_price"] == 10


# ===========================================================================
# TestReferenceClient
# ===========================================================================


class TestReferenceClient:
    async def test_list_markets(
        self, reference_client: ReferenceClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = MARKETS_RESPONSE
        result = await reference_client.list_markets()
        assert isinstance(result, MarketsResponse)
        mock_base_client.get.assert_called_once_with("/v1/ebay/markets")

    async def test_list_categories(
        self, reference_client: ReferenceClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = CATEGORIES_RESPONSE
        result = await reference_client.list_categories()
        assert isinstance(result, CategoriesResponse)
        mock_base_client.get.assert_called_once_with("/v1/ebay/categories")


# ===========================================================================
# TestEbayImports
# ===========================================================================


class TestEbayImports:
    def test_ebay_client_importable(self) -> None:
        from scrapebadger.ebay import EbayClient as _  # noqa: F401

    def test_ebay_client_top_level_importable(self) -> None:
        from scrapebadger import EbayClient as _  # noqa: F401

    def test_ebay_item_top_level_importable(self) -> None:
        from scrapebadger import EbayItem as _  # noqa: F401

    def test_search_response_importable(self) -> None:
        from scrapebadger.ebay import SearchResponse as _  # noqa: F401

    def test_ebay_price_top_level_importable(self) -> None:
        from scrapebadger import EbayPrice as _  # noqa: F401
