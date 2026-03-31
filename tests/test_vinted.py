"""Unit tests for Vinted SDK methods and models.

Tests are organised into:
- TestVintedModels: Pydantic model construction, validation, and immutability
- TestVintedClient: VintedClient sub-client wiring
- TestSearchClient: Search endpoint via mocked HTTP client
- TestItemsClient: Item detail endpoint via mocked HTTP client
- TestUsersClient: User profile and items endpoints via mocked HTTP client
- TestReferenceClient: Brands, colors, statuses, and markets endpoints
- TestVintedImports: Public API importability
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from scrapebadger.vinted.client import VintedClient
from scrapebadger.vinted.items import ItemsClient
from scrapebadger.vinted.models import (
    BrandsResponse,
    ColorsResponse,
    ItemDetailResponse,
    MarketsResponse,
    SearchResponse,
    StatusesResponse,
    UserItemsResponse,
    UserProfileResponse,
    VintedBrand,
    VintedColor,
    VintedItemDetail,
    VintedItemSummary,
    VintedMarket,
    VintedPagination,
    VintedPhoto,
    VintedPrice,
    VintedSellerSummary,
    VintedStatus,
    VintedUserProfile,
    VintedUserSummary,
)
from scrapebadger.vinted.reference import ReferenceClient
from scrapebadger.vinted.search import SearchClient
from scrapebadger.vinted.users import UsersClient

# ---------------------------------------------------------------------------
# Shared sample data
# ---------------------------------------------------------------------------

SAMPLE_PRICE: dict[str, Any] = {"amount": "25.00", "currency_code": "EUR"}

SAMPLE_PHOTO: dict[str, Any] = {
    "id": 1001,
    "url": "https://images.vinted.net/photo1.jpg",
    "dominant_color": "#FF0000",
    "is_main": True,
    "width": 800,
    "height": 600,
    "full_size_url": "https://images.vinted.net/photo1_full.jpg",
}

SAMPLE_USER_SUMMARY: dict[str, Any] = {
    "id": 5001,
    "login": "fashionista42",
    "photo_url": "https://images.vinted.net/avatar.jpg",
    "business": False,
}

SAMPLE_SELLER_SUMMARY: dict[str, Any] = {
    "id": 5001,
    "login": "fashionista42",
    "photo_url": "https://images.vinted.net/avatar.jpg",
    "business": False,
    "feedback_count": 120,
    "feedback_reputation": 0.98,
    "item_count": 45,
    "location": "Paris, France",
    "last_seen": "2026-03-30T12:00:00Z",
    "badges": ["fast_shipper", "trusted_seller"],
}

SAMPLE_ITEM_SUMMARY: dict[str, Any] = {
    "id": 123456789,
    "title": "Nike Air Max 90",
    "price": SAMPLE_PRICE,
    "brand_title": "Nike",
    "size_title": "42",
    "status": "Good",
    "url": "https://www.vinted.fr/items/123456789-nike-air-max-90",
    "favourite_count": 15,
    "view_count": 230,
    "user": SAMPLE_USER_SUMMARY,
    "photo": SAMPLE_PHOTO,
    "photos": [SAMPLE_PHOTO],
}

SAMPLE_ITEM_DETAIL: dict[str, Any] = {
    **SAMPLE_ITEM_SUMMARY,
    "description": "Barely worn Nike Air Max 90, excellent condition",
    "catalog_id": 10,
    "color1": "White",
    "seller": SAMPLE_SELLER_SUMMARY,
    "category": "Shoes",
    "upload_date": "2026-03-15T10:30:00Z",
    "can_buy": True,
    "instant_buy": True,
    "is_closed": False,
    "is_reserved": False,
    "is_hidden": False,
    "size_id": 42,
    "status_id": 2,
    "brand_id": 53,
}

SAMPLE_USER_PROFILE: dict[str, Any] = {
    "id": 5001,
    "login": "fashionista42",
    "photo_url": "https://images.vinted.net/avatar.jpg",
    "business": False,
    "country_code": "FR",
    "city": "Paris",
    "feedback_count": 120,
    "feedback_reputation": 0.98,
    "positive_feedback_count": 115,
    "neutral_feedback_count": 3,
    "negative_feedback_count": 2,
    "item_count": 45,
    "followers_count": 200,
    "following_count": 50,
    "is_online": True,
    "is_on_holiday": False,
    "last_loged_on_ts": "2026-03-30T12:00:00Z",
    "profile_url": "https://www.vinted.fr/member/5001-fashionista42",
    "locale": "fr",
}

SAMPLE_PAGINATION: dict[str, Any] = {
    "current_page": 1,
    "total_pages": 5,
    "total_entries": 98,
    "per_page": 20,
}

SAMPLE_BRAND: dict[str, Any] = {
    "id": 53,
    "title": "Nike",
    "slug": "nike",
    "item_count": 1500000,
    "favourite_count": 50000,
    "is_luxury": False,
    "url": "https://www.vinted.fr/brand/nike",
}

SAMPLE_COLOR: dict[str, Any] = {
    "id": 1,
    "title": "Black",
    "hex": "000000",
    "code": "black",
}

SAMPLE_STATUS: dict[str, Any] = {
    "id": 6,
    "title": "New with tags",
}

SAMPLE_MARKET: dict[str, Any] = {
    "code": "fr",
    "domain": "vinted.fr",
    "country": "France",
    "currency": "EUR",
    "name": "Vinted France",
}

SEARCH_RESPONSE: dict[str, Any] = {
    "items": [SAMPLE_ITEM_SUMMARY],
    "pagination": SAMPLE_PAGINATION,
    "market": "fr",
}

ITEM_DETAIL_RESPONSE: dict[str, Any] = {
    "item": SAMPLE_ITEM_DETAIL,
    "market": "fr",
}

USER_PROFILE_RESPONSE: dict[str, Any] = {
    "user": SAMPLE_USER_PROFILE,
    "market": "fr",
}

USER_ITEMS_RESPONSE: dict[str, Any] = {
    "items": [SAMPLE_ITEM_SUMMARY],
    "pagination": SAMPLE_PAGINATION,
    "market": "fr",
}

BRANDS_RESPONSE: dict[str, Any] = {
    "brands": [SAMPLE_BRAND],
    "pagination": SAMPLE_PAGINATION,
}

COLORS_RESPONSE: dict[str, Any] = {
    "colors": [SAMPLE_COLOR],
}

STATUSES_RESPONSE: dict[str, Any] = {
    "statuses": [SAMPLE_STATUS],
}

MARKETS_RESPONSE: dict[str, Any] = {
    "markets": [SAMPLE_MARKET],
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
def vinted_client(mock_base_client: MagicMock) -> VintedClient:
    """Return a VintedClient backed by a mock base client."""
    return VintedClient(mock_base_client)


@pytest.fixture
def search_client(mock_base_client: MagicMock) -> SearchClient:
    """Return a SearchClient backed by a mock base client."""
    return SearchClient(mock_base_client)


@pytest.fixture
def items_client(mock_base_client: MagicMock) -> ItemsClient:
    """Return an ItemsClient backed by a mock base client."""
    return ItemsClient(mock_base_client)


@pytest.fixture
def users_client(mock_base_client: MagicMock) -> UsersClient:
    """Return a UsersClient backed by a mock base client."""
    return UsersClient(mock_base_client)


@pytest.fixture
def reference_client(mock_base_client: MagicMock) -> ReferenceClient:
    """Return a ReferenceClient backed by a mock base client."""
    return ReferenceClient(mock_base_client)


# ===========================================================================
# TestVintedModels
# ===========================================================================


class TestVintedModels:
    """Pydantic model construction, validation, and immutability tests."""

    # -- Nested models --

    def test_vinted_price(self) -> None:
        price = VintedPrice.model_validate(SAMPLE_PRICE)
        assert price.amount == "25.00"
        assert price.currency_code == "EUR"

    def test_vinted_price_is_frozen(self) -> None:
        price = VintedPrice.model_validate(SAMPLE_PRICE)
        with pytest.raises(Exception):  # noqa: B017
            price.amount = "99.00"  # type: ignore[misc]

    def test_vinted_photo_full(self) -> None:
        photo = VintedPhoto.model_validate(SAMPLE_PHOTO)
        assert photo.id == 1001
        assert photo.url == "https://images.vinted.net/photo1.jpg"
        assert photo.dominant_color == "#FF0000"
        assert photo.is_main is True
        assert photo.width == 800
        assert photo.height == 600
        assert photo.full_size_url == "https://images.vinted.net/photo1_full.jpg"

    def test_vinted_photo_minimal(self) -> None:
        photo = VintedPhoto(id=1, url="https://example.com/p.jpg")
        assert photo.dominant_color is None
        assert photo.is_main is False
        assert photo.width is None

    def test_vinted_user_summary(self) -> None:
        user = VintedUserSummary.model_validate(SAMPLE_USER_SUMMARY)
        assert user.id == 5001
        assert user.login == "fashionista42"
        assert user.business is False

    def test_vinted_user_summary_defaults(self) -> None:
        user = VintedUserSummary(id=1, login="test")
        assert user.photo_url is None
        assert user.business is False

    def test_vinted_seller_summary(self) -> None:
        seller = VintedSellerSummary.model_validate(SAMPLE_SELLER_SUMMARY)
        assert seller.feedback_count == 120
        assert seller.feedback_reputation == 0.98
        assert seller.item_count == 45
        assert seller.location == "Paris, France"
        assert seller.badges == ["fast_shipper", "trusted_seller"]

    def test_vinted_seller_summary_defaults(self) -> None:
        seller = VintedSellerSummary(id=1, login="test")
        assert seller.feedback_count is None
        assert seller.badges == []

    # -- Core models --

    def test_vinted_item_summary(self) -> None:
        item = VintedItemSummary.model_validate(SAMPLE_ITEM_SUMMARY)
        assert item.id == 123456789
        assert item.title == "Nike Air Max 90"
        assert item.price is not None
        assert item.price.amount == "25.00"
        assert item.brand_title == "Nike"
        assert item.favourite_count == 15
        assert item.view_count == 230
        assert item.user is not None
        assert item.user.login == "fashionista42"
        assert len(item.photos) == 1

    def test_vinted_item_summary_minimal(self) -> None:
        item = VintedItemSummary(id=1)
        assert item.title == ""
        assert item.price is None
        assert item.favourite_count == 0
        assert item.photos == []

    def test_vinted_item_summary_is_frozen(self) -> None:
        item = VintedItemSummary.model_validate(SAMPLE_ITEM_SUMMARY)
        with pytest.raises(Exception):  # noqa: B017
            item.title = "mutated"  # type: ignore[misc]

    def test_vinted_item_detail(self) -> None:
        item = VintedItemDetail.model_validate(SAMPLE_ITEM_DETAIL)
        assert item.id == 123456789
        assert item.description == "Barely worn Nike Air Max 90, excellent condition"
        assert item.catalog_id == 10
        assert item.color1 == "White"
        assert item.seller is not None
        assert item.seller.login == "fashionista42"
        assert item.category == "Shoes"
        assert item.can_buy is True
        assert item.instant_buy is True
        assert item.is_closed is False
        assert item.is_reserved is False
        assert item.is_hidden is False
        assert item.size_id == 42
        assert item.status_id == 2
        assert item.brand_id == 53

    def test_vinted_item_detail_minimal(self) -> None:
        item = VintedItemDetail(id=1)
        assert item.description is None
        assert item.seller is None
        assert item.can_buy is None

    def test_vinted_item_detail_is_frozen(self) -> None:
        item = VintedItemDetail.model_validate(SAMPLE_ITEM_DETAIL)
        with pytest.raises(Exception):  # noqa: B017
            item.description = "mutated"  # type: ignore[misc]

    def test_vinted_user_profile(self) -> None:
        user = VintedUserProfile.model_validate(SAMPLE_USER_PROFILE)
        assert user.id == 5001
        assert user.login == "fashionista42"
        assert user.country_code == "FR"
        assert user.city == "Paris"
        assert user.feedback_reputation == 0.98
        assert user.positive_feedback_count == 115
        assert user.neutral_feedback_count == 3
        assert user.negative_feedback_count == 2
        assert user.followers_count == 200
        assert user.following_count == 50
        assert user.is_online is True
        assert user.is_on_holiday is False
        assert user.locale == "fr"

    def test_vinted_user_profile_minimal(self) -> None:
        user = VintedUserProfile(id=1, login="test")
        assert user.country_code is None
        assert user.city is None
        assert user.followers_count is None

    def test_vinted_user_profile_is_frozen(self) -> None:
        user = VintedUserProfile.model_validate(SAMPLE_USER_PROFILE)
        with pytest.raises(Exception):  # noqa: B017
            user.login = "mutated"  # type: ignore[misc]

    # -- Reference models --

    def test_vinted_brand(self) -> None:
        brand = VintedBrand.model_validate(SAMPLE_BRAND)
        assert brand.id == 53
        assert brand.title == "Nike"
        assert brand.slug == "nike"
        assert brand.item_count == 1500000
        assert brand.is_luxury is False

    def test_vinted_brand_minimal(self) -> None:
        brand = VintedBrand(id=1)
        assert brand.title == ""
        assert brand.slug is None

    def test_vinted_color(self) -> None:
        color = VintedColor.model_validate(SAMPLE_COLOR)
        assert color.id == 1
        assert color.title == "Black"
        assert color.hex == "000000"
        assert color.code == "black"

    def test_vinted_status(self) -> None:
        status = VintedStatus.model_validate(SAMPLE_STATUS)
        assert status.id == 6
        assert status.title == "New with tags"

    def test_vinted_market(self) -> None:
        market = VintedMarket.model_validate(SAMPLE_MARKET)
        assert market.code == "fr"
        assert market.domain == "vinted.fr"
        assert market.country == "France"
        assert market.currency == "EUR"
        assert market.name == "Vinted France"

    def test_vinted_market_minimal(self) -> None:
        market = VintedMarket(code="de")
        assert market.domain is None
        assert market.name is None

    # -- Pagination --

    def test_vinted_pagination(self) -> None:
        pagination = VintedPagination.model_validate(SAMPLE_PAGINATION)
        assert pagination.current_page == 1
        assert pagination.total_pages == 5
        assert pagination.total_entries == 98
        assert pagination.per_page == 20

    def test_vinted_pagination_defaults(self) -> None:
        pagination = VintedPagination()
        assert pagination.current_page == 1
        assert pagination.total_pages == 1
        assert pagination.total_entries == 0
        assert pagination.per_page == 20

    # -- Response envelopes --

    def test_search_response(self) -> None:
        resp = SearchResponse.model_validate(SEARCH_RESPONSE)
        assert len(resp.items) == 1
        assert resp.items[0].id == 123456789
        assert resp.pagination is not None
        assert resp.pagination.total_entries == 98
        assert resp.market == "fr"

    def test_search_response_empty(self) -> None:
        resp = SearchResponse.model_validate({"items": [], "market": "de"})
        assert resp.items == []
        assert resp.pagination is None

    def test_item_detail_response(self) -> None:
        resp = ItemDetailResponse.model_validate(ITEM_DETAIL_RESPONSE)
        assert resp.item is not None
        assert resp.item.id == 123456789
        assert resp.item.description is not None
        assert resp.market == "fr"

    def test_item_detail_response_null_item(self) -> None:
        resp = ItemDetailResponse.model_validate({"item": None, "market": "fr"})
        assert resp.item is None

    def test_user_profile_response(self) -> None:
        resp = UserProfileResponse.model_validate(USER_PROFILE_RESPONSE)
        assert resp.user is not None
        assert resp.user.id == 5001
        assert resp.market == "fr"

    def test_user_items_response(self) -> None:
        resp = UserItemsResponse.model_validate(USER_ITEMS_RESPONSE)
        assert len(resp.items) == 1
        assert resp.pagination is not None
        assert resp.market == "fr"

    def test_brands_response(self) -> None:
        resp = BrandsResponse.model_validate(BRANDS_RESPONSE)
        assert len(resp.brands) == 1
        assert resp.brands[0].title == "Nike"

    def test_brands_response_empty(self) -> None:
        resp = BrandsResponse.model_validate({"brands": []})
        assert resp.brands == []
        assert resp.pagination is None

    def test_colors_response(self) -> None:
        resp = ColorsResponse.model_validate(COLORS_RESPONSE)
        assert len(resp.colors) == 1
        assert resp.colors[0].title == "Black"

    def test_colors_response_empty(self) -> None:
        resp = ColorsResponse.model_validate({"colors": []})
        assert resp.colors == []

    def test_statuses_response(self) -> None:
        resp = StatusesResponse.model_validate(STATUSES_RESPONSE)
        assert len(resp.statuses) == 1
        assert resp.statuses[0].title == "New with tags"

    def test_markets_response(self) -> None:
        resp = MarketsResponse.model_validate(MARKETS_RESPONSE)
        assert len(resp.markets) == 1
        assert resp.markets[0].code == "fr"

    def test_markets_response_empty(self) -> None:
        resp = MarketsResponse.model_validate({"markets": []})
        assert resp.markets == []


# ===========================================================================
# TestVintedClient
# ===========================================================================


class TestVintedClient:
    """Tests for VintedClient sub-client wiring."""

    def test_search_property(self, vinted_client: VintedClient) -> None:
        assert isinstance(vinted_client.search, SearchClient)

    def test_items_property(self, vinted_client: VintedClient) -> None:
        assert isinstance(vinted_client.items, ItemsClient)

    def test_users_property(self, vinted_client: VintedClient) -> None:
        assert isinstance(vinted_client.users, UsersClient)

    def test_reference_property(self, vinted_client: VintedClient) -> None:
        assert isinstance(vinted_client.reference, ReferenceClient)

    def test_sub_clients_are_stable(self, vinted_client: VintedClient) -> None:
        """Sub-client properties return the same instance on repeated access."""
        assert vinted_client.search is vinted_client.search
        assert vinted_client.items is vinted_client.items
        assert vinted_client.users is vinted_client.users
        assert vinted_client.reference is vinted_client.reference


# ===========================================================================
# TestSearchClient
# ===========================================================================


class TestSearchClient:
    """Tests for SearchClient methods."""

    async def test_search_default_params(
        self, search_client: SearchClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = SEARCH_RESPONSE
        result = await search_client.search("nike air max")

        assert isinstance(result, SearchResponse)
        assert len(result.items) == 1
        assert result.items[0].title == "Nike Air Max 90"

        mock_base_client.get.assert_called_once()
        call_args = mock_base_client.get.call_args
        assert call_args[0][0] == "/v1/vinted/search"
        params = call_args[1]["params"]
        assert params["query"] == "nike air max"
        assert params["market"] == "fr"
        assert params["page"] == 1
        assert params["per_page"] == 20

    async def test_search_with_filters(
        self, search_client: SearchClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = SEARCH_RESPONSE
        await search_client.search(
            "vintage jacket",
            market="de",
            page=2,
            per_page=40,
            price_from="10",
            price_to="100",
            brand_ids="53,72",
            color_ids="1,2",
            status_ids="6",
            order="newest_first",
        )

        params = mock_base_client.get.call_args[1]["params"]
        assert params["market"] == "de"
        assert params["page"] == 2
        assert params["per_page"] == 40
        assert params["price_from"] == "10"
        assert params["price_to"] == "100"
        assert params["brand_ids"] == "53,72"
        assert params["color_ids"] == "1,2"
        assert params["status_ids"] == "6"
        assert params["order"] == "newest_first"

    async def test_search_optional_params_default_none(
        self, search_client: SearchClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = SEARCH_RESPONSE
        await search_client.search("test")

        params = mock_base_client.get.call_args[1]["params"]
        assert params["price_from"] is None
        assert params["price_to"] is None
        assert params["brand_ids"] is None
        assert params["color_ids"] is None
        assert params["status_ids"] is None
        assert params["order"] is None

    async def test_search_returns_search_response(
        self, search_client: SearchClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = SEARCH_RESPONSE
        result = await search_client.search("test")
        assert isinstance(result, SearchResponse)


# ===========================================================================
# TestItemsClient
# ===========================================================================


class TestItemsClient:
    """Tests for ItemsClient methods."""

    async def test_get_item_default_market(
        self, items_client: ItemsClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = ITEM_DETAIL_RESPONSE
        result = await items_client.get(123456789)

        assert isinstance(result, ItemDetailResponse)
        assert result.item is not None
        assert result.item.id == 123456789
        assert result.item.description is not None

        mock_base_client.get.assert_called_once()
        call_args = mock_base_client.get.call_args
        assert call_args[0][0] == "/v1/vinted/items/123456789"
        assert call_args[1]["params"]["market"] == "fr"

    async def test_get_item_custom_market(
        self, items_client: ItemsClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = ITEM_DETAIL_RESPONSE
        await items_client.get(123456789, market="de")

        params = mock_base_client.get.call_args[1]["params"]
        assert params["market"] == "de"

    async def test_get_item_returns_item_detail_response(
        self, items_client: ItemsClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = ITEM_DETAIL_RESPONSE
        result = await items_client.get(123456789)
        assert isinstance(result, ItemDetailResponse)


# ===========================================================================
# TestUsersClient
# ===========================================================================


class TestUsersClient:
    """Tests for UsersClient methods."""

    # -- get_profile --

    async def test_get_profile_default_market(
        self, users_client: UsersClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = USER_PROFILE_RESPONSE
        result = await users_client.get_profile(5001)

        assert isinstance(result, UserProfileResponse)
        assert result.user is not None
        assert result.user.id == 5001
        assert result.user.login == "fashionista42"

        mock_base_client.get.assert_called_once()
        call_args = mock_base_client.get.call_args
        assert call_args[0][0] == "/v1/vinted/users/5001"
        assert call_args[1]["params"]["market"] == "fr"

    async def test_get_profile_custom_market(
        self, users_client: UsersClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = USER_PROFILE_RESPONSE
        await users_client.get_profile(5001, market="de")

        params = mock_base_client.get.call_args[1]["params"]
        assert params["market"] == "de"

    # -- get_items --

    async def test_get_items_default_params(
        self, users_client: UsersClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = USER_ITEMS_RESPONSE
        result = await users_client.get_items(5001)

        assert isinstance(result, UserItemsResponse)
        assert len(result.items) == 1

        call_args = mock_base_client.get.call_args
        assert call_args[0][0] == "/v1/vinted/users/5001/items"
        params = call_args[1]["params"]
        assert params["market"] == "fr"
        assert params["page"] == 1
        assert params["per_page"] == 20

    async def test_get_items_with_pagination(
        self, users_client: UsersClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = USER_ITEMS_RESPONSE
        await users_client.get_items(5001, market="de", page=3, per_page=40)

        params = mock_base_client.get.call_args[1]["params"]
        assert params["market"] == "de"
        assert params["page"] == 3
        assert params["per_page"] == 40

    async def test_get_items_returns_user_items_response(
        self, users_client: UsersClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = USER_ITEMS_RESPONSE
        result = await users_client.get_items(5001)
        assert isinstance(result, UserItemsResponse)


# ===========================================================================
# TestReferenceClient
# ===========================================================================


class TestReferenceClient:
    """Tests for ReferenceClient methods."""

    # -- brands --

    async def test_brands_default_params(
        self, reference_client: ReferenceClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = BRANDS_RESPONSE
        result = await reference_client.brands()

        assert isinstance(result, BrandsResponse)
        assert len(result.brands) == 1
        assert result.brands[0].title == "Nike"

        call_args = mock_base_client.get.call_args
        assert call_args[0][0] == "/v1/vinted/brands"
        params = call_args[1]["params"]
        assert params["keyword"] is None
        assert params["market"] == "fr"
        assert params["per_page"] == 20

    async def test_brands_with_keyword(
        self, reference_client: ReferenceClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = BRANDS_RESPONSE
        await reference_client.brands("adidas", market="de", per_page=10)

        params = mock_base_client.get.call_args[1]["params"]
        assert params["keyword"] == "adidas"
        assert params["market"] == "de"
        assert params["per_page"] == 10

    # -- colors --

    async def test_colors_default_market(
        self, reference_client: ReferenceClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = COLORS_RESPONSE
        result = await reference_client.colors()

        assert isinstance(result, ColorsResponse)
        assert len(result.colors) == 1

        call_args = mock_base_client.get.call_args
        assert call_args[0][0] == "/v1/vinted/colors"
        assert call_args[1]["params"]["market"] == "fr"

    async def test_colors_custom_market(
        self, reference_client: ReferenceClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = COLORS_RESPONSE
        await reference_client.colors(market="de")

        assert mock_base_client.get.call_args[1]["params"]["market"] == "de"

    # -- statuses --

    async def test_statuses_default_market(
        self, reference_client: ReferenceClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = STATUSES_RESPONSE
        result = await reference_client.statuses()

        assert isinstance(result, StatusesResponse)
        assert len(result.statuses) == 1
        assert result.statuses[0].title == "New with tags"

        call_args = mock_base_client.get.call_args
        assert call_args[0][0] == "/v1/vinted/statuses"
        assert call_args[1]["params"]["market"] == "fr"

    async def test_statuses_custom_market(
        self, reference_client: ReferenceClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = STATUSES_RESPONSE
        await reference_client.statuses(market="uk")

        assert mock_base_client.get.call_args[1]["params"]["market"] == "uk"

    # -- markets --

    async def test_markets(
        self, reference_client: ReferenceClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = MARKETS_RESPONSE
        result = await reference_client.markets()

        assert isinstance(result, MarketsResponse)
        assert len(result.markets) == 1
        assert result.markets[0].code == "fr"

        mock_base_client.get.assert_called_once_with("/v1/vinted/markets")

    async def test_markets_empty(
        self, reference_client: ReferenceClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = {"markets": []}
        result = await reference_client.markets()
        assert result.markets == []


# ===========================================================================
# TestVintedImports
# ===========================================================================


class TestVintedImports:
    """Tests that Vinted types are importable from the vinted package."""

    def test_vinted_client_importable(self) -> None:
        from scrapebadger.vinted import VintedClient as _  # noqa: F401

    def test_search_response_importable(self) -> None:
        from scrapebadger.vinted import SearchResponse as _  # noqa: F401

    def test_item_detail_response_importable(self) -> None:
        from scrapebadger.vinted import ItemDetailResponse as _  # noqa: F401

    def test_user_profile_response_importable(self) -> None:
        from scrapebadger.vinted import UserProfileResponse as _  # noqa: F401

    def test_user_items_response_importable(self) -> None:
        from scrapebadger.vinted import UserItemsResponse as _  # noqa: F401

    def test_brands_response_importable(self) -> None:
        from scrapebadger.vinted import BrandsResponse as _  # noqa: F401

    def test_colors_response_importable(self) -> None:
        from scrapebadger.vinted import ColorsResponse as _  # noqa: F401

    def test_statuses_response_importable(self) -> None:
        from scrapebadger.vinted import StatusesResponse as _  # noqa: F401

    def test_markets_response_importable(self) -> None:
        from scrapebadger.vinted import MarketsResponse as _  # noqa: F401

    def test_vinted_item_summary_importable(self) -> None:
        from scrapebadger.vinted import VintedItemSummary as _  # noqa: F401

    def test_vinted_item_detail_importable(self) -> None:
        from scrapebadger.vinted import VintedItemDetail as _  # noqa: F401

    def test_vinted_user_profile_importable(self) -> None:
        from scrapebadger.vinted import VintedUserProfile as _  # noqa: F401

    def test_vinted_price_importable(self) -> None:
        from scrapebadger.vinted import VintedPrice as _  # noqa: F401

    def test_vinted_photo_importable(self) -> None:
        from scrapebadger.vinted import VintedPhoto as _  # noqa: F401

    def test_vinted_brand_importable(self) -> None:
        from scrapebadger.vinted import VintedBrand as _  # noqa: F401

    def test_vinted_color_importable(self) -> None:
        from scrapebadger.vinted import VintedColor as _  # noqa: F401

    def test_vinted_market_importable(self) -> None:
        from scrapebadger.vinted import VintedMarket as _  # noqa: F401

    def test_vinted_pagination_importable(self) -> None:
        from scrapebadger.vinted import VintedPagination as _  # noqa: F401

    def test_vinted_item_summary_top_level_importable(self) -> None:
        from scrapebadger import VintedItemSummary as _  # noqa: F401

    def test_vinted_price_top_level_importable(self) -> None:
        from scrapebadger import VintedPrice as _  # noqa: F401
