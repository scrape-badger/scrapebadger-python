"""Unit tests for Amazon SDK methods and models.

Tests cover:
- TestAmazonModels: Pydantic model construction, validation, immutability, aliases
- TestAmazonClient: AmazonClient sub-client wiring
- TestSearchClient / TestProductsClient / TestListingsClient / TestSellersClient /
  TestReferenceClient: endpoint routing via a mocked HTTP client
- TestAmazonImports: public API importability
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from scrapebadger.amazon.client import AmazonClient
from scrapebadger.amazon.listings import ListingsClient
from scrapebadger.amazon.models import (
    AmazonPrice,
    AutocompleteResponse,
    Bestseller,
    BestsellersResponse,
    CategoriesResponse,
    CategoryResponse,
    DealsResponse,
    MarketsResponse,
    NewReleasesResponse,
    Offer,
    OffersResponse,
    Product,
    ProductDetailResponse,
    RatingBreakdown,
    Review,
    ReviewsResponse,
    SearchResponse,
    SearchResult,
    Seller,
    SellerFeedbackResponse,
    SellerFeedbackSummary,
    SellerProductsResponse,
    SellerProfileResponse,
)
from scrapebadger.amazon.products import ProductsClient
from scrapebadger.amazon.reference import ReferenceClient
from scrapebadger.amazon.search import SearchClient
from scrapebadger.amazon.sellers import SellersClient

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
    "asin": "B08N5WRWNW",
    "title": "Echo Dot (4th Gen)",
    "link": "https://www.amazon.com/dp/B08N5WRWNW",
    "image": "https://m.media-amazon.com/images/I/abc.jpg",
    "price": SAMPLE_PRICE,
    "list_price": {"value": 49.99, "currency": "USD", "symbol": "$", "raw": "$49.99"},
    "unit_price": None,
    "rating": 4.7,
    "ratings_total": 123456,
    "is_prime": True,
    "is_sponsored": False,
    "is_amazons_choice": True,
    "is_best_seller": False,
    "bought_past_month": "10K+ bought in past month",
    "coupon": "Save 5%",
    "availability": "In Stock",
}

SAMPLE_PRODUCT: dict[str, Any] = {
    "asin": "B08N5WRWNW",
    "parent_asin": "B08N5KWB9H",
    "title": "Echo Dot (4th Gen)",
    "link": "https://www.amazon.com/dp/B08N5WRWNW",
    "brand": "Amazon",
    "brand_url": "https://www.amazon.com/stores/Amazon",
    "manufacturer": "Amazon",
    "model_number": "B7W64E",
    "price": SAMPLE_PRICE,
    "list_price": {"value": 49.99, "currency": "USD", "symbol": "$", "raw": "$49.99"},
    "savings_amount": {"value": 20.0, "currency": "USD", "symbol": "$", "raw": "$20.00"},
    "discount_percent": 40.0,
    "rating": 4.7,
    "ratings_total": 123456,
    "rating_breakdown": {
        "five_star": 80,
        "four_star": 10,
        "three_star": 5,
        "two_star": 3,
        "one_star": 2,
    },
    "bought_past_month": "10K+ bought in past month",
    "in_stock": True,
    "availability": "In Stock",
    "feature_bullets": ["Meet Echo Dot", "Voice control"],
    "description": "Our most popular smart speaker.",
    "main_image": "https://m.media-amazon.com/images/I/main.jpg",
    "images": ["https://m.media-amazon.com/images/I/1.jpg"],
    "images_count": 1,
    "videos": [],
    "videos_count": 0,
    "has_aplus_content": True,
    "variants": [
        {
            "asin": "B08N5WRWNW",
            "attributes": {"Color": "Charcoal"},
            "price": SAMPLE_PRICE,
            "is_current": True,
        }
    ],
    "variant_asins": ["B08N5WRWNW", "B08N5KWB9H"],
    "categories": ["Electronics", "Smart Home"],
    "bestsellers_rank": [
        {"rank": 1, "category": "Smart Speakers", "link": "https://example.com/bsr"}
    ],
    "attributes": {"Connectivity": "Wi-Fi"},
    "specifications": {"Weight": "0.75 lb"},
    "dimensions": "3.9 x 3.9 x 3.5 inches",
    "weight": "0.75 lb",
    "first_available": "October 22, 2020",
    "country_of_origin": "China",
    "buybox": {
        "seller_name": "Amazon.com",
        "seller_id": "ATVPDKIKX0DER",
        "price": SAMPLE_PRICE,
        "fulfillment": "Ships from and sold by Amazon.com",
    },
    "sold_by": "Amazon.com",
    "ships_from": "Amazon.com",
    "fulfilled_by": "Amazon",
    "is_amazon_seller": True,
    "badges": {
        "amazons_choice": True,
        "amazons_choice_keyword": "echo dot",
        "best_seller": False,
        "prime": True,
        "climate_pledge_friendly": True,
    },
    "coupon": {"text": "Save 5%", "discount": "5%"},
    "deal": {"type": "lightning", "price": SAMPLE_PRICE, "ends_at": "2026-06-04T00:00:00Z"},
    "delivery": {"message": "FREE delivery", "date": "Tomorrow", "is_free": True},
    "frequently_bought_together": [
        {
            "asin": "B07XJ8C8F5",
            "title": "Smart Plug",
            "link": "https://www.amazon.com/dp/B07XJ8C8F5",
            "image": "https://m.media-amazon.com/images/I/plug.jpg",
            "price": SAMPLE_PRICE,
        }
    ],
    "also_bought": [],
    "answered_questions": 42,
    "top_reviews": [
        {
            "id": "R1ABCDEF",
            "title": "Great speaker",
            "body": "Works perfectly.",
            "rating": 5.0,
            "verified_purchase": True,
        }
    ],
    "scraped_utc": 1751500000.0,
    "scraped_at": "2026-06-03T00:00:00Z",
}

SAMPLE_OFFER: dict[str, Any] = {
    "position": 1,
    "seller": {
        "name": "Amazon.com",
        "id": "ATVPDKIKX0DER",
        "link": "https://www.amazon.com/sp?seller=ATVPDKIKX0DER",
        "rating": 4.8,
        "ratings_total": 1000000,
        "ratings_percentage_positive": 98,
    },
    "price": SAMPLE_PRICE,
    "condition": {"is_new": True, "title": "New", "comments": None},
    "delivery": {
        "is_free": True,
        "fulfilled_by_amazon": True,
        "date": "Tomorrow",
        "price": None,
    },
    "buybox_winner": True,
    "is_prime": True,
    "minimum_order_quantity": 1,
    "maximum_order_quantity": 30,
}

SAMPLE_REVIEW: dict[str, Any] = {
    "id": "R1ABCDEF",
    "title": "Great speaker",
    "body": "Works perfectly.",
    "rating": 5.0,
    "date_raw": "Reviewed in the United States on June 1, 2026",
    "date_utc": 1751328000.0,
    "date_at": "2026-06-01T00:00:00Z",
    "review_country": "United States",
    "is_global_review": False,
    "profile": {
        "name": "Jane",
        "link": "https://www.amazon.com/profile/x",
        "id": "AXYZ",
        "image": "https://m.media-amazon.com/images/I/jane.jpg",
    },
    "verified_purchase": True,
    "vine_program": False,
    "helpful_votes": 12,
    "variant": "Charcoal",
    "images": ["https://m.media-amazon.com/images/I/review.jpg"],
}

SAMPLE_BESTSELLER: dict[str, Any] = {
    "rank": 1,
    "position": 1,
    "asin": "B08N5WRWNW",
    "title": "Echo Dot (4th Gen)",
    "link": "https://www.amazon.com/dp/B08N5WRWNW",
    "image": "https://m.media-amazon.com/images/I/abc.jpg",
    "rating": 4.7,
    "ratings_total": 123456,
    "price": SAMPLE_PRICE,
}

SAMPLE_DEAL: dict[str, Any] = {
    "position": 1,
    "asin": "B08N5WRWNW",
    "title": "Echo Dot (4th Gen)",
    "link": "https://www.amazon.com/dp/B08N5WRWNW",
    "image": "https://m.media-amazon.com/images/I/abc.jpg",
    "deal_price": SAMPLE_PRICE,
    "list_price": {"value": 49.99, "currency": "USD", "symbol": "$", "raw": "$49.99"},
    "discount_percent": 40.0,
    "deal_type": "Lightning Deal",
    "is_lightning_deal": True,
    "badge": "Limited time deal",
    "ends_at_utc": 1751500000.0,
    "ends_at": "2026-06-04T00:00:00Z",
}

SAMPLE_SELLER: dict[str, Any] = {
    "seller_id": "A2L77EE7U53NWQ",
    "name": "Amazon Warehouse",
    "link": "https://www.amazon.com/sp?seller=A2L77EE7U53NWQ",
    "rating": 4.6,
    "ratings_total": 500000,
    "ratings_percentage_positive": 95,
    "feedback": {
        "lifetime": {"positive": 95, "neutral": 3, "negative": 2, "count": 500000},
        "12mo": {"positive": 96, "neutral": 2, "negative": 2, "count": 100000},
        "90d": {"positive": 97, "neutral": 2, "negative": 1, "count": 30000},
        "30d": {"positive": 98, "neutral": 1, "negative": 1, "count": 10000},
    },
    "business_name": "Amazon.com Services LLC",
    "business_address": "410 Terry Ave N, Seattle, WA",
    "member_since": "January 1, 2000",
}

SAMPLE_FEEDBACK_ENTRY: dict[str, Any] = {
    "rating": 5.0,
    "comment": "Fast shipping",
    "rater": "buyer123",
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
    "name": "Amazon US",
}

SAMPLE_CATEGORY: dict[str, Any] = {
    "name": "Electronics",
    "alias": "electronics",
    "search_alias": "electronics",
    "bestseller_node": "172282",
}

SAMPLE_PAGINATION: dict[str, Any] = {
    "current_page": 1,
    "total_pages": 20,
    "total_results": 400,
}

SEARCH_RESPONSE: dict[str, Any] = {
    "query": "echo dot",
    "domain": "com",
    "results": [SAMPLE_SEARCH_RESULT],
    "pagination": SAMPLE_PAGINATION,
    "scraped_utc": 1751500000.0,
    "scraped_at": "2026-06-03T00:00:00Z",
}

PRODUCT_DETAIL_RESPONSE: dict[str, Any] = {"domain": "com", "product": SAMPLE_PRODUCT}

OFFERS_RESPONSE: dict[str, Any] = {
    "asin": "B08N5WRWNW",
    "domain": "com",
    "buybox": SAMPLE_OFFER,
    "offers": [SAMPLE_OFFER],
    "total_offers": 1,
    "scraped_utc": 1751500000.0,
    "scraped_at": "2026-06-03T00:00:00Z",
}

REVIEWS_RESPONSE: dict[str, Any] = {
    "asin": "B08N5WRWNW",
    "domain": "com",
    "reviews": [SAMPLE_REVIEW],
    "rating": 4.7,
    "ratings_total": 123456,
    "rating_breakdown": {
        "five_star": 80,
        "four_star": 10,
        "three_star": 5,
        "two_star": 3,
        "one_star": 2,
    },
    "pagination": SAMPLE_PAGINATION,
    "scraped_utc": 1751500000.0,
    "scraped_at": "2026-06-03T00:00:00Z",
}

BESTSELLERS_RESPONSE: dict[str, Any] = {
    "domain": "com",
    "category": "electronics",
    "bestsellers": [SAMPLE_BESTSELLER],
    "pagination": SAMPLE_PAGINATION,
    "scraped_utc": 1751500000.0,
    "scraped_at": "2026-06-03T00:00:00Z",
}

NEW_RELEASES_RESPONSE: dict[str, Any] = {
    "domain": "com",
    "category": "books",
    "new_releases": [SAMPLE_BESTSELLER],
    "pagination": SAMPLE_PAGINATION,
}

DEALS_RESPONSE: dict[str, Any] = {
    "domain": "com",
    "category": None,
    "deals": [SAMPLE_DEAL],
    "pagination": SAMPLE_PAGINATION,
}

CATEGORY_RESPONSE: dict[str, Any] = {
    "domain": "com",
    "node": "172282",
    "results": [SAMPLE_SEARCH_RESULT],
    "pagination": SAMPLE_PAGINATION,
}

SELLER_PROFILE_RESPONSE: dict[str, Any] = {"domain": "com", "seller": SAMPLE_SELLER}

SELLER_PRODUCTS_RESPONSE: dict[str, Any] = {
    "domain": "com",
    "seller_id": "A2L77EE7U53NWQ",
    "products": [SAMPLE_SEARCH_RESULT],
    "pagination": SAMPLE_PAGINATION,
}

SELLER_FEEDBACK_RESPONSE: dict[str, Any] = {
    "domain": "com",
    "seller_id": "A2L77EE7U53NWQ",
    "feedback": [SAMPLE_FEEDBACK_ENTRY],
    "pagination": SAMPLE_PAGINATION,
}

AUTOCOMPLETE_RESPONSE: dict[str, Any] = {
    "query": "echo",
    "domain": "com",
    "suggestions": [{"value": "echo dot", "alias": "electronics"}, {"value": "echo show"}],
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
def amazon_client(mock_base_client: MagicMock) -> AmazonClient:
    return AmazonClient(mock_base_client)


@pytest.fixture
def search_client(mock_base_client: MagicMock) -> SearchClient:
    return SearchClient(mock_base_client)


@pytest.fixture
def products_client(mock_base_client: MagicMock) -> ProductsClient:
    return ProductsClient(mock_base_client)


@pytest.fixture
def listings_client(mock_base_client: MagicMock) -> ListingsClient:
    return ListingsClient(mock_base_client)


@pytest.fixture
def sellers_client(mock_base_client: MagicMock) -> SellersClient:
    return SellersClient(mock_base_client)


@pytest.fixture
def reference_client(mock_base_client: MagicMock) -> ReferenceClient:
    return ReferenceClient(mock_base_client)


# ===========================================================================
# TestAmazonModels
# ===========================================================================


class TestAmazonModels:
    """Pydantic model construction, validation, immutability, and alias tests."""

    def test_amazon_price(self) -> None:
        price = AmazonPrice.model_validate(SAMPLE_PRICE)
        assert price.value == 29.99
        assert price.currency == "USD"
        assert price.symbol == "$"
        assert price.raw == "$29.99"

    def test_amazon_price_defaults(self) -> None:
        price = AmazonPrice()
        assert price.value is None
        assert price.currency is None

    def test_amazon_price_is_frozen(self) -> None:
        price = AmazonPrice.model_validate(SAMPLE_PRICE)
        with pytest.raises(Exception):  # noqa: B017
            price.value = 1.0  # type: ignore[misc]

    def test_search_result(self) -> None:
        result = SearchResult.model_validate(SAMPLE_SEARCH_RESULT)
        assert result.position == 1
        assert result.asin == "B08N5WRWNW"
        assert result.price is not None
        assert result.price.value == 29.99
        assert result.is_prime is True
        assert result.is_amazons_choice is True

    def test_search_result_minimal(self) -> None:
        result = SearchResult(position=1, asin="X")
        assert result.title is None
        assert result.is_prime is False
        assert result.price is None

    def test_product_full(self) -> None:
        product = Product.model_validate(SAMPLE_PRODUCT)
        assert product.asin == "B08N5WRWNW"
        assert product.parent_asin == "B08N5KWB9H"
        assert product.brand_url == "https://www.amazon.com/stores/Amazon"
        assert len(product.top_reviews) == 1
        assert product.top_reviews[0].id == "R1ABCDEF"
        assert product.top_reviews[0].rating == 5.0
        assert product.top_reviews[0].verified_purchase is True
        assert product.rating_breakdown is not None
        assert product.rating_breakdown.five_star == 80
        assert len(product.variants) == 1
        assert product.variants[0].attributes == {"Color": "Charcoal"}
        assert product.badges.amazons_choice is True
        assert product.badges.amazons_choice_keyword == "echo dot"
        assert product.buybox is not None
        assert product.buybox.seller_id == "ATVPDKIKX0DER"
        assert product.coupon is not None
        assert product.coupon.discount == "5%"
        assert product.deal is not None
        assert product.delivery is not None
        assert product.delivery.is_free is True
        assert len(product.frequently_bought_together) == 1
        assert product.bestsellers_rank[0].rank == 1
        assert product.scraped_utc == 1751500000.0
        assert product.scraped_at == "2026-06-03T00:00:00Z"

    def test_product_minimal(self) -> None:
        product = Product(asin="X")
        assert product.title is None
        assert product.brand_url is None
        assert product.top_reviews == []
        assert product.feature_bullets == []
        assert product.images == []
        assert product.images_count == 0
        assert product.has_aplus_content is False
        # badges default-factory yields a ProductBadges instance
        assert product.badges.prime is False

    def test_product_is_frozen(self) -> None:
        product = Product.model_validate(SAMPLE_PRODUCT)
        with pytest.raises(Exception):  # noqa: B017
            product.title = "mutated"  # type: ignore[misc]

    def test_rating_breakdown(self) -> None:
        rb = RatingBreakdown.model_validate(
            {"five_star": 50, "four_star": 25, "three_star": 15, "two_star": 5, "one_star": 5}
        )
        assert rb.five_star == 50
        assert rb.one_star == 5

    def test_offer_full(self) -> None:
        offer = Offer.model_validate(SAMPLE_OFFER)
        assert offer.position == 1
        assert offer.seller is not None
        assert offer.seller.ratings_percentage_positive == 98
        assert offer.condition is not None
        assert offer.condition.is_new is True
        assert offer.delivery is not None
        assert offer.delivery.fulfilled_by_amazon is True
        assert offer.buybox_winner is True
        assert offer.minimum_order_quantity == 1
        assert offer.maximum_order_quantity == 30

    def test_review_full(self) -> None:
        review = Review.model_validate(SAMPLE_REVIEW)
        assert review.id == "R1ABCDEF"
        assert review.rating == 5.0
        assert review.date_utc == 1751328000.0
        assert review.date_at == "2026-06-01T00:00:00Z"
        assert review.profile is not None
        assert review.profile.name == "Jane"
        assert review.verified_purchase is True
        assert review.images == ["https://m.media-amazon.com/images/I/review.jpg"]

    def test_bestseller(self) -> None:
        bs = Bestseller.model_validate(SAMPLE_BESTSELLER)
        assert bs.rank == 1
        assert bs.position == 1
        assert bs.asin == "B08N5WRWNW"
        assert bs.price is not None

    def test_seller_feedback_summary_aliases(self) -> None:
        """The 12mo/90d/30d wire aliases must populate twelve/ninety/thirty fields."""
        summary = SellerFeedbackSummary.model_validate(SAMPLE_SELLER["feedback"])
        assert summary.lifetime is not None
        assert summary.lifetime.count == 500000
        assert summary.twelve_month is not None
        assert summary.twelve_month.count == 100000
        assert summary.ninety_day is not None
        assert summary.ninety_day.count == 30000
        assert summary.thirty_day is not None
        assert summary.thirty_day.count == 10000

    def test_seller_feedback_summary_by_name(self) -> None:
        """populate_by_name allows the python field names too."""
        summary = SellerFeedbackSummary.model_validate(
            {"twelve_month": {"count": 7}, "ninety_day": {"count": 3}}
        )
        assert summary.twelve_month is not None
        assert summary.twelve_month.count == 7
        assert summary.ninety_day is not None
        assert summary.ninety_day.count == 3

    def test_seller_full(self) -> None:
        seller = Seller.model_validate(SAMPLE_SELLER)
        assert seller.seller_id == "A2L77EE7U53NWQ"
        assert seller.ratings_percentage_positive == 95
        assert seller.feedback is not None
        assert seller.feedback.thirty_day is not None
        assert seller.feedback.thirty_day.positive == 98

    # -- Response envelopes --

    def test_search_response(self) -> None:
        resp = SearchResponse.model_validate(SEARCH_RESPONSE)
        assert resp.query == "echo dot"
        assert resp.domain == "com"
        assert len(resp.results) == 1
        assert resp.pagination.current_page == 1
        assert resp.scraped_utc == 1751500000.0

    def test_search_response_defaults(self) -> None:
        resp = SearchResponse.model_validate({"query": "x", "domain": "com"})
        assert resp.results == []
        assert resp.pagination.current_page == 1
        assert resp.scraped_utc is None

    def test_product_detail_response(self) -> None:
        resp = ProductDetailResponse.model_validate(PRODUCT_DETAIL_RESPONSE)
        assert resp.domain == "com"
        assert resp.product.asin == "B08N5WRWNW"

    def test_offers_response(self) -> None:
        resp = OffersResponse.model_validate(OFFERS_RESPONSE)
        assert resp.asin == "B08N5WRWNW"
        assert resp.buybox is not None
        assert resp.buybox.buybox_winner is True
        assert len(resp.offers) == 1
        assert resp.total_offers == 1

    def test_reviews_response(self) -> None:
        resp = ReviewsResponse.model_validate(REVIEWS_RESPONSE)
        assert resp.asin == "B08N5WRWNW"
        assert len(resp.reviews) == 1
        assert resp.rating == 4.7
        assert resp.rating_breakdown is not None
        assert resp.rating_breakdown.five_star == 80

    def test_bestsellers_response(self) -> None:
        resp = BestsellersResponse.model_validate(BESTSELLERS_RESPONSE)
        assert resp.category == "electronics"
        assert len(resp.bestsellers) == 1

    def test_new_releases_response(self) -> None:
        resp = NewReleasesResponse.model_validate(NEW_RELEASES_RESPONSE)
        assert resp.category == "books"
        assert len(resp.new_releases) == 1

    def test_deals_response(self) -> None:
        resp = DealsResponse.model_validate(DEALS_RESPONSE)
        assert len(resp.deals) == 1
        assert resp.deals[0].is_lightning_deal is True
        assert resp.deals[0].ends_at_utc == 1751500000.0

    def test_category_response(self) -> None:
        resp = CategoryResponse.model_validate(CATEGORY_RESPONSE)
        assert resp.node == "172282"
        assert len(resp.results) == 1

    def test_seller_profile_response(self) -> None:
        resp = SellerProfileResponse.model_validate(SELLER_PROFILE_RESPONSE)
        assert resp.seller.seller_id == "A2L77EE7U53NWQ"

    def test_seller_products_response(self) -> None:
        resp = SellerProductsResponse.model_validate(SELLER_PRODUCTS_RESPONSE)
        assert resp.seller_id == "A2L77EE7U53NWQ"
        assert len(resp.products) == 1

    def test_seller_feedback_response(self) -> None:
        resp = SellerFeedbackResponse.model_validate(SELLER_FEEDBACK_RESPONSE)
        assert resp.seller_id == "A2L77EE7U53NWQ"
        assert len(resp.feedback) == 1
        assert resp.feedback[0].rating == 5.0

    def test_autocomplete_response(self) -> None:
        resp = AutocompleteResponse.model_validate(AUTOCOMPLETE_RESPONSE)
        assert resp.query == "echo"
        assert len(resp.suggestions) == 2
        assert resp.suggestions[0].value == "echo dot"
        assert resp.suggestions[1].alias is None

    def test_markets_response(self) -> None:
        resp = MarketsResponse.model_validate(MARKETS_RESPONSE)
        assert len(resp.markets) == 1
        assert resp.markets[0].code == "US"
        assert resp.markets[0].locale == "en-US"

    def test_categories_response(self) -> None:
        resp = CategoriesResponse.model_validate(CATEGORIES_RESPONSE)
        assert len(resp.categories) == 1
        assert resp.categories[0].alias == "electronics"
        assert resp.categories[0].bestseller_node == "172282"

    def test_ignores_unknown_fields(self) -> None:
        resp = MarketsResponse.model_validate({"markets": [], "unexpected": 123})
        assert resp.markets == []


# ===========================================================================
# TestAmazonClient
# ===========================================================================


class TestAmazonClient:
    """Tests for AmazonClient sub-client wiring."""

    def test_search_property(self, amazon_client: AmazonClient) -> None:
        assert isinstance(amazon_client.search, SearchClient)

    def test_products_property(self, amazon_client: AmazonClient) -> None:
        assert isinstance(amazon_client.products, ProductsClient)

    def test_listings_property(self, amazon_client: AmazonClient) -> None:
        assert isinstance(amazon_client.listings, ListingsClient)

    def test_sellers_property(self, amazon_client: AmazonClient) -> None:
        assert isinstance(amazon_client.sellers, SellersClient)

    def test_reference_property(self, amazon_client: AmazonClient) -> None:
        assert isinstance(amazon_client.reference, ReferenceClient)

    def test_sub_clients_are_stable(self, amazon_client: AmazonClient) -> None:
        assert amazon_client.search is amazon_client.search
        assert amazon_client.products is amazon_client.products
        assert amazon_client.listings is amazon_client.listings
        assert amazon_client.sellers is amazon_client.sellers
        assert amazon_client.reference is amazon_client.reference


# ===========================================================================
# TestSearchClient
# ===========================================================================


class TestSearchClient:
    async def test_search_default_params(
        self, search_client: SearchClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = SEARCH_RESPONSE
        result = await search_client.search("echo dot")

        assert isinstance(result, SearchResponse)
        call_args = mock_base_client.get.call_args
        assert call_args[0][0] == "/v1/amazon/search"
        params = call_args[1]["params"]
        assert params["query"] == "echo dot"
        assert params["domain"] == "com"
        assert params["page"] == 1
        assert params["sort_by"] is None
        assert params["min_price"] is None

    async def test_search_with_filters(
        self, search_client: SearchClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = SEARCH_RESPONSE
        await search_client.search(
            "laptop",
            domain="de",
            page=2,
            sort_by="price_low_to_high",
            category="electronics",
            min_price=100,
            max_price=500,
            zip="10115",
            language="de_DE",
        )
        params = mock_base_client.get.call_args[1]["params"]
        assert params["domain"] == "de"
        assert params["page"] == 2
        assert params["sort_by"] == "price_low_to_high"
        assert params["category"] == "electronics"
        assert params["min_price"] == 100
        assert params["max_price"] == 500
        assert params["zip"] == "10115"
        assert params["language"] == "de_DE"

    async def test_autocomplete(
        self, search_client: SearchClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = AUTOCOMPLETE_RESPONSE
        result = await search_client.autocomplete("echo", domain="co.uk")
        assert isinstance(result, AutocompleteResponse)
        call_args = mock_base_client.get.call_args
        assert call_args[0][0] == "/v1/amazon/autocomplete"
        assert call_args[1]["params"]["query"] == "echo"
        assert call_args[1]["params"]["domain"] == "co.uk"


# ===========================================================================
# TestProductsClient
# ===========================================================================


class TestProductsClient:
    async def test_get(self, products_client: ProductsClient, mock_base_client: MagicMock) -> None:
        mock_base_client.get.return_value = PRODUCT_DETAIL_RESPONSE
        result = await products_client.get("B08N5WRWNW", domain="de", zip="10115", language="de_DE")
        assert isinstance(result, ProductDetailResponse)
        assert result.product.asin == "B08N5WRWNW"
        call_args = mock_base_client.get.call_args
        assert call_args[0][0] == "/v1/amazon/products/B08N5WRWNW"
        params = call_args[1]["params"]
        assert params["domain"] == "de"
        assert params["zip"] == "10115"
        assert params["language"] == "de_DE"

    async def test_offers(
        self, products_client: ProductsClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = OFFERS_RESPONSE
        result = await products_client.offers("B08N5WRWNW")
        assert isinstance(result, OffersResponse)
        assert mock_base_client.get.call_args[0][0] == "/v1/amazon/products/B08N5WRWNW/offers"

    async def test_reviews(
        self, products_client: ProductsClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = REVIEWS_RESPONSE
        result = await products_client.reviews(
            "B08N5WRWNW", sort_by="recent", star="five_star", verified_only=True, media_only=False
        )
        assert isinstance(result, ReviewsResponse)
        call_args = mock_base_client.get.call_args
        assert call_args[0][0] == "/v1/amazon/products/B08N5WRWNW/reviews"
        params = call_args[1]["params"]
        assert params["sort_by"] == "recent"
        assert params["star"] == "five_star"
        assert params["verified_only"] is True
        assert params["media_only"] is False


# ===========================================================================
# TestListingsClient
# ===========================================================================


class TestListingsClient:
    async def test_bestsellers(
        self, listings_client: ListingsClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = BESTSELLERS_RESPONSE
        result = await listings_client.bestsellers(category="electronics", page=2)
        assert isinstance(result, BestsellersResponse)
        call_args = mock_base_client.get.call_args
        assert call_args[0][0] == "/v1/amazon/bestsellers"
        assert call_args[1]["params"]["category"] == "electronics"
        assert call_args[1]["params"]["page"] == 2

    async def test_new_releases(
        self, listings_client: ListingsClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = NEW_RELEASES_RESPONSE
        result = await listings_client.new_releases(category="books")
        assert isinstance(result, NewReleasesResponse)
        assert mock_base_client.get.call_args[0][0] == "/v1/amazon/new-releases"

    async def test_deals(
        self, listings_client: ListingsClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = DEALS_RESPONSE
        result = await listings_client.deals()
        assert isinstance(result, DealsResponse)
        assert mock_base_client.get.call_args[0][0] == "/v1/amazon/deals"

    async def test_category(
        self, listings_client: ListingsClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = CATEGORY_RESPONSE
        result = await listings_client.category("172282", sort_by="featured")
        assert isinstance(result, CategoryResponse)
        call_args = mock_base_client.get.call_args
        assert call_args[0][0] == "/v1/amazon/category"
        assert call_args[1]["params"]["node"] == "172282"
        assert call_args[1]["params"]["sort_by"] == "featured"


# ===========================================================================
# TestSellersClient
# ===========================================================================


class TestSellersClient:
    async def test_get(self, sellers_client: SellersClient, mock_base_client: MagicMock) -> None:
        mock_base_client.get.return_value = SELLER_PROFILE_RESPONSE
        result = await sellers_client.get("A2L77EE7U53NWQ")
        assert isinstance(result, SellerProfileResponse)
        assert mock_base_client.get.call_args[0][0] == "/v1/amazon/sellers/A2L77EE7U53NWQ"

    async def test_products(
        self, sellers_client: SellersClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = SELLER_PRODUCTS_RESPONSE
        result = await sellers_client.products("A2L77EE7U53NWQ", page=3)
        assert isinstance(result, SellerProductsResponse)
        call_args = mock_base_client.get.call_args
        assert call_args[0][0] == "/v1/amazon/sellers/A2L77EE7U53NWQ/products"
        assert call_args[1]["params"]["page"] == 3

    async def test_feedback(
        self, sellers_client: SellersClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = SELLER_FEEDBACK_RESPONSE
        result = await sellers_client.feedback("A2L77EE7U53NWQ")
        assert isinstance(result, SellerFeedbackResponse)
        assert mock_base_client.get.call_args[0][0] == "/v1/amazon/sellers/A2L77EE7U53NWQ/feedback"


# ===========================================================================
# TestReferenceClient
# ===========================================================================


class TestReferenceClient:
    async def test_markets(
        self, reference_client: ReferenceClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = MARKETS_RESPONSE
        result = await reference_client.markets()
        assert isinstance(result, MarketsResponse)
        mock_base_client.get.assert_called_once_with("/v1/amazon/markets")

    async def test_categories(
        self, reference_client: ReferenceClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = CATEGORIES_RESPONSE
        result = await reference_client.categories()
        assert isinstance(result, CategoriesResponse)
        mock_base_client.get.assert_called_once_with("/v1/amazon/categories")


# ===========================================================================
# TestAmazonImports
# ===========================================================================


class TestAmazonImports:
    def test_amazon_client_importable(self) -> None:
        from scrapebadger.amazon import AmazonClient as _  # noqa: F401

    def test_amazon_client_top_level_importable(self) -> None:
        from scrapebadger import AmazonClient as _  # noqa: F401

    def test_product_top_level_importable(self) -> None:
        from scrapebadger import Product as _  # noqa: F401

    def test_search_response_importable(self) -> None:
        from scrapebadger.amazon import SearchResponse as _  # noqa: F401

    def test_amazon_price_top_level_importable(self) -> None:
        from scrapebadger import AmazonPrice as _  # noqa: F401
