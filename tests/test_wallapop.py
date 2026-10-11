"""Unit tests for Wallapop SDK methods and models.

Payloads are the ScrapeBadger API's normalised output (``wallapop_scraper``
models), produced from the scraper's recorded Wallapop fixtures.

Tests cover:
- TestWallapopModels: Pydantic model construction, validation, immutability
- TestWallapopClient: endpoint routing and param handling via a mocked HTTP client
- TestWallapopRegistration: top-level client property and public exports
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from scrapebadger import ScrapeBadger
from scrapebadger.wallapop.client import WallapopClient
from scrapebadger.wallapop.models import (
    AutocompleteResponse,
    CategoriesResponse,
    FilterOptionsResponse,
    FiltersResponse,
    ItemDetail,
    MarketsResponse,
    ReviewsResponse,
    SearchItem,
    SearchResponse,
    UserItemsResponse,
    UserProfile,
)

# ---------------------------------------------------------------------------
# Shared sample data (normalised API output)
# ---------------------------------------------------------------------------

SEARCH_ITEM: dict[str, Any] = {
    "id": "nzxeknm5x562",
    "user_id": "dqjwdd53wwzo",
    "title": "iPhone 14 128GB Negro",
    "description": "iPhone 14 de color negro, con 128GB de almacenamiento.",
    "price": 250.0,
    "currency": "EUR",
    "category_id": 24200,
    "taxonomy": [
        {"id": 24200, "name": "Tecnología y electrónica"},
        {"id": 24201, "name": "Telefonía: móviles y smartwatches"},
        {"id": 9447, "name": "Smartphones"},
    ],
    "condition": None,
    "brand": None,
    "model": None,
    "attributes": {},
    "images": [
        {
            "id": "e65ve2rg0l2j",
            "small": "https://cdn.wallapop.com/images/10420/lo/q3/__/c10420p1311318554/i6787540572.jpg?pictureSize=W320",
            "medium": "https://cdn.wallapop.com/images/10420/lo/q3/__/c10420p1311318554/i6787540572.jpg?pictureSize=W640",
            "large": "https://cdn.wallapop.com/images/10420/lo/q3/__/c10420p1311318554/i6787540572.jpg?pictureSize=W800",
            "average_color": "13C1AC",
        }
    ],
    "location": {
        "latitude": 40.47122907944395,
        "longitude": -3.8786801592876357,
        "postal_code": "28222",
        "city": "Majadahonda",
        "region": "Comunidad de Madrid",
        "region2": "Madrid",
        "country_code": "ES",
        "approximated": None,
    },
    "shippable": True,
    "user_allows_shipping": True,
    "reserved": False,
    "bumped": True,
    "bump_type": "city",
    "is_top_profile": True,
    "is_refurbished": False,
    "has_warranty": False,
    "slug": "iphone-14-128gb-1311318554",
    "url": "https://es.wallapop.com/item/iphone-14-128gb-1311318554",
    "created_utc": 1791580490.949,
    "created_at": "2026-10-09T21:14:50.949000Z",
    "modified_utc": 1791753563.082,
    "modified_at": "2026-10-11T21:19:23.082000Z",
}

SEARCH_CAR_ITEM: dict[str, Any] = {
    "id": "wzyr2ol4o565",
    "user_id": "dqjwy89qn4zo",
    "title": "SEAT Leon 2017 150CV 1.4tsi 83000km",
    "description": "Atención compraventas no quiero ni que me contactéis ",
    "price": 15500.0,
    "currency": "EUR",
    "category_id": 100,
    "taxonomy": [{"id": 100, "name": "Cars"}],
    "condition": None,
    "brand": "SEAT",
    "model": "Leon",
    "attributes": {
        "brand": "SEAT",
        "model": "Leon",
        "year": 2017,
        "version": "1.4 TSI ACT 150 FR Plus 5p S/S",
        "km": 83000,
        "engine": "Gasoline",
        "gearbox": "Manual",
        "horsepower": 150.0,
    },
    "images": [
        {
            "id": "p61vde303m76",
            "small": "https://cdn.wallapop.com/images/10420/ln/gt/__/c10420p1309205044/i6773783355.jpg?pictureSize=W320",
            "medium": "https://cdn.wallapop.com/images/10420/ln/gt/__/c10420p1309205044/i6773783355.jpg?pictureSize=W640",
            "large": "https://cdn.wallapop.com/images/10420/ln/gt/__/c10420p1309205044/i6773783355.jpg?pictureSize=W800",
            "average_color": "13C1AC",
        }
    ],
    "location": {
        "latitude": 40.42199997804331,
        "longitude": -3.690143996872792,
        "postal_code": "28014",
        "city": "Madrid",
        "region": "Comunidad de Madrid",
        "region2": "Madrid",
        "country_code": "ES",
        "approximated": None,
    },
    "shippable": False,
    "user_allows_shipping": False,
    "reserved": False,
    "bumped": True,
    "bump_type": "city",
    "is_top_profile": False,
    "is_refurbished": False,
    "has_warranty": False,
    "slug": "seat-leon-2017-1309205044",
    "url": "https://es.wallapop.com/item/seat-leon-2017-1309205044",
    "created_utc": 1791123788.513,
    "created_at": "2026-10-04T14:23:08.513000Z",
    "modified_utc": 1791712679.702,
    "modified_at": "2026-10-11T09:57:59.702000Z",
}

ITEM_DETAIL: dict[str, Any] = {
    "id": "nzxeknm5x562",
    "user_id": "dqjwdd53wwzo",
    "title": "iPhone 14 128GB Negro",
    "description": "iPhone 14 de color negro, con 128GB de almacenamiento.",
    "vertical": "consumer_goods",
    "price": 250.0,
    "currency": "EUR",
    "category_id": 9447,
    "taxonomy": [
        {"id": 24200, "name": "Tecnología y electrónica"},
        {"id": 24201, "name": "Telefonía: móviles y smartwatches"},
        {"id": 9447, "name": "Smartphones"},
    ],
    "condition": "good",
    "brand": "Apple",
    "model": "iPhone 14",
    "attributes": {
        "color": {"value": "black", "title": "Color", "text": "Negro"},
        "condition": {"value": "good", "title": "Estado", "text": "Buen estado"},
        "model": {"value": "iPhone 14", "title": "Modelo", "text": "iPhone 14"},
        "brand": {"value": "Apple", "title": "Marca", "text": "Apple"},
        "storage_capacity": {
            "value": "128gb",
            "title": "Capacidad de almacenamiento",
            "text": "128 GB",
        },
        "up_to_kg": {"value": "1.0", "title": "Kg", "text": "1.0"},
    },
    "characteristics": "Buen estado · Apple · iPhone 14 · 128 GB · Negro",
    "characteristics_details": [
        {"attribute": "Modelo", "value": "iPhone 14"},
        {"attribute": "Color", "value": "Negro"},
    ],
    "hashtags": [],
    "images": [
        {
            "id": "e65ve2rg0l2j",
            "small": "https://cdn.wallapop.com/images/10420/lo/q3/__/c10420p1311318554/i6787540572.jpg?pictureSize=W320",
            "medium": "https://cdn.wallapop.com/images/10420/lo/q3/__/c10420p1311318554/i6787540572.jpg?pictureSize=W640",
            "large": "https://cdn.wallapop.com/images/10420/lo/q3/__/c10420p1311318554/i6787540572.jpg?pictureSize=W800",
            "average_color": "13C1AC",
        }
    ],
    "location": {
        "latitude": 40.47122907944395,
        "longitude": -3.8786801592876357,
        "postal_code": "28222",
        "city": "Majadahonda",
        "region": None,
        "region2": None,
        "country_code": "ES",
        "approximated": True,
    },
    "shippable": True,
    "user_allows_shipping": True,
    "supports_shipping": True,
    "bumped": True,
    "bump_type": "city",
    "is_top_profile": True,
    "views": 225,
    "favorites": 14,
    "conversations": 4,
    "slug": "iphone-14-128gb-1311318554",
    "url": "https://es.wallapop.com/item/iphone-14-128gb-1311318554",
    "modified_utc": 1791753563.0,
    "modified_at": "2026-10-11T21:19:23Z",
}

USER_PROFILE: dict[str, Any] = {
    "id": "dqjwdd53wwzo",
    "name": "Alejandro C.",
    "type": "normal",
    "seller_type": "Private",
    "verified": True,
    "is_top_profile": True,
    "featured": False,
    "image": {
        "id": "0j2w7pmkmdjy",
        "small": "https://cdn.wallapop.com/images/13/0e/yb/__/c13p25115753/i333760311.jpg?pictureSize=W320",
        "medium": "https://cdn.wallapop.com/images/13/0e/yb/__/c13p25115753/i333760311.jpg?pictureSize=W640",
        "large": "https://cdn.wallapop.com/images/13/0e/yb/__/c13p25115753/i333760311.jpg?pictureSize=W800",
        "average_color": "5b5651",
    },
    "location": {
        "latitude": 40.47122907944395,
        "longitude": -3.8786801592876357,
        "postal_code": "28222",
        "city": "Majadahonda",
        "region": None,
        "region2": None,
        "country_code": "ES",
        "approximated": False,
    },
    "rating_average": 4.9,
    "scoring_stars": 98.0,
    "reviews_count": 108,
    "published_count": 6,
    "sold_count": 107,
    "sells_count": 121,
    "buys_count": 40,
    "reports_received_count": 14,
    "response_rate": "less_than_one_hour",
    "activity_level": "unknown",
    "deliveries_on_time_in_days": 0,
    "validations": {
        "level": "partially_verified",
        "email": True,
        "mobile": False,
        "facebook": False,
        "google": True,
        "picture": True,
        "location": True,
        "birthday": True,
        "kyc": True,
    },
    "slug": "alexc-25115753",
    "url": "https://es.wallapop.com/user/alexc-25115753",
    "registered_utc": 1442055921.0,
    "registered_at": "2015-09-12T11:05:21Z",
}

USER_ITEM: dict[str, Any] = {
    "id": "3zlm3y52kpjx",
    "title": "Caja Cooler Master c700m",
    "description": "En buen estado , valorada en 300€ , nueva 600€ , le falta solo una pata de "
    "goma ",
    "price": 150.0,
    "currency": "EUR",
    "category_id": 24200,
    "condition": "good",
    "attributes": {"brand": "Cooler Master ", "condition": "good", "up_to_kg": "30.0"},
    "images": [
        {
            "id": "0j2wey3lm2rj",
            "small": "https://cdn.wallapop.com/images/10420/lf/ul/__/c10420p1296410893/i6706063683.jpg?pictureSize=W320",
            "medium": "https://cdn.wallapop.com/images/10420/lf/ul/__/c10420p1296410893/i6706063683.jpg?pictureSize=W640",
            "large": "https://cdn.wallapop.com/images/10420/lf/ul/__/c10420p1296410893/i6706063683.jpg?pictureSize=W800",
            "average_color": "13C1AC",
        }
    ],
    "shippable": True,
    "user_allows_shipping": True,
    "is_refurbished": False,
    "has_warranty": False,
    "slug": "caja-cooler-master-c700m-1296410893",
    "url": "https://es.wallapop.com/item/caja-cooler-master-c700m-1296410893",
}

REVIEW: dict[str, Any] = {
    "id": "7035191d-0156-40e3-90c3-736a0bf6f24c",
    "rating": 5,
    "scoring": 100,
    "comment": "Muy agradable y super facil de hacer tratos con el, lo recomiendo al 100%, se "
    "preocupa mucho.",
    "type": "sell",
    "is_shipping_transaction": True,
    "item": {
        "id": "3zlmy547v8jx",
        "title": "Sony Alpha a6400 Cámara Mirrorless APS-C",
        "category_id": 24200,
        "image": "https://cdn.wallapop.com/images/10420/li/xd/__/c10420p1301579669/i6739066786.jpg?pictureSize=W800",
        "slug": "sony-alpha-a6400-camara-mirrorless-aps-c-1301579669",
        "url": "https://es.wallapop.com/item/sony-alpha-a6400-camara-mirrorless-aps-c-1301579669",
    },
    "reviewer": {
        "id": "pj9yxer3go6e",
        "name": "Markel L.",
        "image": "https://cdn.wallapop.com/images/13/7f/qs/__/c13p449707485/i3608964288.jpg?pictureSize=W800",
        "slug": "unknown-449707485",
    },
    "created_utc": 1790438569.0,
    "created_at": "2026-09-26T16:02:49Z",
}

SUGGESTIONS: list[dict[str, Any]] = [
    {"text": "bicicleta look", "subtitle": None, "type": "regular"},
    {"text": "bicis", "subtitle": None, "type": "regular"},
    {"text": "bicicleta niños", "subtitle": None, "type": "regular"},
]

CATEGORY: dict[str, Any] = {
    "id": 100,
    "name": "Cars",
    "parent_id": None,
    "vertical": "cars",
    "icon": "car",
    "subcategories": [],
}

FILTERS: list[dict[str, Any]] = [
    {
        "id": "is_shippable",
        "title": "Opciones de envío",
        "type": "toggle",
        "params": ["is_shippable"],
        "multi": None,
        "options": [],
        "options_endpoint": False,
    },
    {
        "id": "time_filter",
        "title": "Fecha de publicación",
        "type": "list",
        "params": ["time_filter"],
        "multi": False,
        "options": [
            {"id": "today", "title": "Hoy"},
            {"id": "lastWeek", "title": "Últimos 7 días"},
            {"id": "lastMonth", "title": "Últimos 30 días"},
        ],
        "options_endpoint": False,
    },
    {
        "id": "price",
        "title": "Precio",
        "type": "slider",
        "params": ["min_sale_price", "max_sale_price"],
        "multi": None,
        "options": [],
        "options_endpoint": False,
    },
    {
        "id": "brand",
        "title": "Marca",
        "type": "list",
        "params": ["brand"],
        "multi": True,
        "options": [],
        "options_endpoint": True,
    },
]

FILTER_OPTIONS: list[dict[str, Any]] = [
    {"id": "2K", "title": "2K"},
    {"id": "2K Games", "title": "2K Games"},
    {"id": "2NLF", "title": "2NLF"},
]

NEXT_PAGE: str = "eyJhbGciOiJIUzI1NiJ9.eyJwYXJhbXMiOnsic2VhcmNoUmVxdWVzdFBhcmF..."

USER_ITEMS_NEXT: str = "SSMxMjg3NDgyMTc1X0RfVSMyNTUwMTU0Nl9QIzIwMjYtMTAtMDJUMTI6NDE6NTQuOTY3Wg=="

SEARCH_RESPONSE: dict[str, Any] = {
    "items": [SEARCH_ITEM, SEARCH_CAR_ITEM],
    "result_count": 2,
    "total_results": 49093,
    "next_page": NEXT_PAGE,
    "order_by": "most_relevance",
    "market": "es",
    "country_code": "ES",
    "search_id": "a6e9213a-8d01-481f-8f3d-bd6ffaf2a61c",
}

USER_ITEMS_RESPONSE: dict[str, Any] = {
    "user_id": "dqjwdd53wwzo",
    "items": [USER_ITEM],
    "result_count": 1,
    "next_page": USER_ITEMS_NEXT,
    "market": "es",
}

REVIEWS_RESPONSE: dict[str, Any] = {
    "user_id": "dqjwdd53wwzo",
    "reviews": [REVIEW],
    "result_count": 1,
    "next_page": "40",
    "market": "es",
}

AUTOCOMPLETE_RESPONSE: dict[str, Any] = {
    "query": "bici",
    "suggestions": SUGGESTIONS,
    "market": "es",
}

CATEGORIES_RESPONSE: dict[str, Any] = {
    "categories": [
        CATEGORY,
        {
            "id": 24200,
            "name": "Tecnología y electrónica",
            "parent_id": None,
            "vertical": "consumer_goods",
            "icon": "tech",
            "subcategories": [
                {
                    "id": 24201,
                    "name": "Telefonía: móviles y smartwatches",
                    "parent_id": 24200,
                    "vertical": "consumer_goods",
                    "icon": None,
                    "subcategories": [],
                }
            ],
        },
    ],
    "market": "es",
}

FILTERS_RESPONSE: dict[str, Any] = {"filters": FILTERS, "market": "es"}

FILTER_OPTIONS_RESPONSE: dict[str, Any] = {
    "filter_id": "brand",
    "options": FILTER_OPTIONS,
    "market": "es",
}

MARKETS_RESPONSE: dict[str, Any] = {
    "markets": [
        {
            "code": "es",
            "country_code": "ES",
            "name": "Spain",
            "currency": "EUR",
            "language": "es",
            "default_latitude": 40.4168,
            "default_longitude": -3.7038,
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
def wallapop_client(mock_base_client: MagicMock) -> WallapopClient:
    return WallapopClient(mock_base_client)


def _call(mock: MagicMock) -> tuple[str, dict[str, Any] | None]:
    args = mock.get.call_args
    return args[0][0], args[1].get("params")


# ===========================================================================
# TestWallapopModels
# ===========================================================================


class TestWallapopModels:
    """Pydantic model construction, validation, and immutability tests."""

    def test_search_response(self) -> None:
        resp = SearchResponse.model_validate(SEARCH_RESPONSE)
        assert resp.result_count == 2
        assert resp.total_results == 49093
        assert resp.next_page == NEXT_PAGE
        assert resp.country_code == "ES"
        item = resp.items[0]
        assert item.id == "nzxeknm5x562"
        assert item.price == 250.0
        assert item.taxonomy[-1].name == "Smartphones"
        assert item.images[0].average_color == "13C1AC"
        assert item.location is not None
        assert item.location.city == "Majadahonda"
        assert item.bumped is True
        assert item.created_at == "2026-10-09T21:14:50.949000Z"

    def test_search_car_attributes(self) -> None:
        car = SearchItem.model_validate(SEARCH_CAR_ITEM)
        assert car.brand == "SEAT"
        assert car.attributes["year"] == 2017
        assert car.attributes["km"] == 83000
        assert car.attributes["gearbox"] == "Manual"

    def test_item_detail(self) -> None:
        item = ItemDetail.model_validate(ITEM_DETAIL)
        assert item.vertical == "consumer_goods"
        assert item.condition == "good"
        assert item.attributes["condition"].text == "Buen estado"
        assert item.attributes["storage_capacity"].value == "128gb"
        assert item.characteristics_details[0] == {"attribute": "Modelo", "value": "iPhone 14"}
        assert item.views == 225
        assert item.favorites == 14
        assert item.location is not None
        assert item.location.approximated is True

    def test_user_profile(self) -> None:
        user = UserProfile.model_validate(USER_PROFILE)
        assert user.name == "Alejandro C."
        assert user.rating_average == 4.9
        assert user.scoring_stars == 98.0
        assert user.sold_count == 107
        assert user.response_rate == "less_than_one_hour"
        assert user.validations is not None
        assert user.validations.level == "partially_verified"
        assert user.validations.kyc is True
        assert user.image is not None
        assert user.registered_at == "2015-09-12T11:05:21Z"

    def test_user_items_response(self) -> None:
        resp = UserItemsResponse.model_validate(USER_ITEMS_RESPONSE)
        assert resp.user_id == "dqjwdd53wwzo"
        assert resp.items[0].attributes["up_to_kg"] == "30.0"
        assert resp.next_page == USER_ITEMS_NEXT

    def test_reviews_response(self) -> None:
        resp = ReviewsResponse.model_validate(REVIEWS_RESPONSE)
        review = resp.reviews[0]
        assert review.rating == 5
        assert review.type == "sell"
        assert review.item is not None
        assert review.item.title == "Sony Alpha a6400 Cámara Mirrorless APS-C"
        assert review.reviewer is not None
        assert review.reviewer.name == "Markel L."

    def test_reference_responses(self) -> None:
        auto = AutocompleteResponse.model_validate(AUTOCOMPLETE_RESPONSE)
        assert auto.suggestions[0].text == "bicicleta look"
        cats = CategoriesResponse.model_validate(CATEGORIES_RESPONSE)
        assert cats.categories[0].vertical == "cars"
        assert cats.categories[1].subcategories[0].parent_id == 24200
        filters = FiltersResponse.model_validate(FILTERS_RESPONSE)
        by_id = {f.id: f for f in filters.filters}
        assert by_id["time_filter"].options[1].id == "lastWeek"
        assert by_id["brand"].options_endpoint is True
        assert by_id["price"].params == ["min_sale_price", "max_sale_price"]
        opts = FilterOptionsResponse.model_validate(FILTER_OPTIONS_RESPONSE)
        assert opts.options[0].title == "2K"
        markets = MarketsResponse.model_validate(MARKETS_RESPONSE)
        assert markets.markets[0].default_latitude == 40.4168

    def test_minimal_defaults(self) -> None:
        resp = SearchResponse.model_validate({"market": "es"})
        assert resp.items == []
        assert resp.result_count == 0
        assert resp.next_page is None
        item = SearchItem(id="x")
        assert item.bumped is False
        assert item.attributes == {}

    def test_is_frozen(self) -> None:
        item = ItemDetail.model_validate(ITEM_DETAIL)
        with pytest.raises(Exception):  # noqa: B017
            item.title = "mutated"  # type: ignore[misc]

    def test_ignores_unknown_fields(self) -> None:
        resp = SearchResponse.model_validate({"market": "es", "unexpected": 1})
        assert resp.market == "es"


# ===========================================================================
# TestWallapopClient
# ===========================================================================


class TestWallapopClient:
    async def test_search_defaults(
        self, wallapop_client: WallapopClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = SEARCH_RESPONSE
        result = await wallapop_client.search("iphone 14")
        assert isinstance(result, SearchResponse)
        assert _call(mock_base_client) == (
            "/v1/wallapop/search",
            {"query": "iphone 14", "market": "es"},
        )

    async def test_search_all_filters(
        self, wallapop_client: WallapopClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = SEARCH_RESPONSE
        await wallapop_client.search(
            "seat leon",
            market="it",
            latitude=41.9,
            longitude=12.5,
            distance_km=50,
            category_id=100,
            min_price=0,
            max_price=20000,
            condition="good,as_good_as_new",
            brand="SEAT",
            model="Leon",
            color="black",
            time_filter="lastWeek",
            shippable=True,
            has_warranty=True,
            refurbished=True,
            min_year=2015,
            max_year=2020,
            min_km=0,
            max_km=100000,
            gearbox="manual",
            min_horsepower=100,
            max_horsepower=200,
            order_by="price_low_to_high",
        )
        _, params = _call(mock_base_client)
        assert params == {
            "query": "seat leon",
            "market": "it",
            "latitude": 41.9,
            "longitude": 12.5,
            "distance_km": 50,
            "category_id": 100,
            "min_price": 0,
            "max_price": 20000,
            "condition": "good,as_good_as_new",
            "brand": "SEAT",
            "model": "Leon",
            "color": "black",
            "time_filter": "lastWeek",
            "shippable": True,
            "has_warranty": True,
            "refurbished": True,
            "min_year": 2015,
            "max_year": 2020,
            "min_km": 0,
            "max_km": 100000,
            "gearbox": "manual",
            "min_horsepower": 100,
            "max_horsepower": 200,
            "order_by": "price_low_to_high",
        }

    async def test_search_false_booleans_not_sent(
        self, wallapop_client: WallapopClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = SEARCH_RESPONSE
        await wallapop_client.search(category_id=100, shippable=False)
        _, params = _call(mock_base_client)
        assert params == {"market": "es", "category_id": 100}

    async def test_search_next_page(
        self, wallapop_client: WallapopClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = SEARCH_RESPONSE
        await wallapop_client.search(next_page=NEXT_PAGE)
        _, params = _call(mock_base_client)
        assert params == {"market": "es", "next_page": NEXT_PAGE}

    async def test_get_item(
        self, wallapop_client: WallapopClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = ITEM_DETAIL
        result = await wallapop_client.get_item("nzxeknm5x562", market="pt")
        assert isinstance(result, ItemDetail)
        assert _call(mock_base_client) == ("/v1/wallapop/items/nzxeknm5x562", {"market": "pt"})

    async def test_get_user(
        self, wallapop_client: WallapopClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = USER_PROFILE
        result = await wallapop_client.get_user("alexc-25115753")
        assert isinstance(result, UserProfile)
        assert _call(mock_base_client) == ("/v1/wallapop/users/alexc-25115753", {"market": "es"})

    async def test_get_user_items(
        self, wallapop_client: WallapopClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = USER_ITEMS_RESPONSE
        result = await wallapop_client.get_user_items("dqjwdd53wwzo")
        assert isinstance(result, UserItemsResponse)
        assert _call(mock_base_client) == (
            "/v1/wallapop/users/dqjwdd53wwzo/items",
            {"market": "es"},
        )
        await wallapop_client.get_user_items("dqjwdd53wwzo", next_page=USER_ITEMS_NEXT)
        _, params = _call(mock_base_client)
        assert params == {"market": "es", "next_page": USER_ITEMS_NEXT}

    async def test_get_user_reviews(
        self, wallapop_client: WallapopClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = REVIEWS_RESPONSE
        result = await wallapop_client.get_user_reviews("dqjwdd53wwzo", next_page="40")
        assert isinstance(result, ReviewsResponse)
        assert _call(mock_base_client) == (
            "/v1/wallapop/users/dqjwdd53wwzo/reviews",
            {"market": "es", "next_page": "40"},
        )

    async def test_autocomplete(
        self, wallapop_client: WallapopClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = AUTOCOMPLETE_RESPONSE
        result = await wallapop_client.autocomplete("bici")
        assert isinstance(result, AutocompleteResponse)
        assert _call(mock_base_client) == (
            "/v1/wallapop/autocomplete",
            {"query": "bici", "market": "es"},
        )

    async def test_list_categories(
        self, wallapop_client: WallapopClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = CATEGORIES_RESPONSE
        result = await wallapop_client.list_categories(market="it")
        assert isinstance(result, CategoriesResponse)
        assert _call(mock_base_client) == ("/v1/wallapop/categories", {"market": "it"})

    async def test_list_filters(
        self, wallapop_client: WallapopClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = FILTERS_RESPONSE
        result = await wallapop_client.list_filters()
        assert isinstance(result, FiltersResponse)
        assert _call(mock_base_client) == ("/v1/wallapop/filters", {"market": "es"})
        await wallapop_client.list_filters(category_id=24200, query="iphone")
        _, params = _call(mock_base_client)
        assert params == {"category_id": 24200, "query": "iphone", "market": "es"}

    async def test_list_filter_options(
        self, wallapop_client: WallapopClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = FILTER_OPTIONS_RESPONSE
        result = await wallapop_client.list_filter_options("brand", query="iphone")
        assert isinstance(result, FilterOptionsResponse)
        assert _call(mock_base_client) == (
            "/v1/wallapop/filters/brand/options",
            {"query": "iphone", "market": "es"},
        )

    async def test_list_markets(
        self, wallapop_client: WallapopClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = MARKETS_RESPONSE
        result = await wallapop_client.list_markets()
        assert isinstance(result, MarketsResponse)
        mock_base_client.get.assert_called_once_with("/v1/wallapop/markets")


# ===========================================================================
# TestWallapopRegistration
# ===========================================================================


class TestWallapopRegistration:
    def test_property_is_cached(self) -> None:
        client = ScrapeBadger(api_key="test")
        assert isinstance(client.wallapop, WallapopClient)
        assert client.wallapop is client.wallapop

    def test_public_exports(self) -> None:
        import scrapebadger

        for name in (
            "WallapopClient",
            "WallapopSearchResponse",
            "WallapopItemDetail",
            "WallapopUserProfile",
            "WallapopReviewsResponse",
            "WallapopMarketsResponse",
        ):
            assert name in scrapebadger.__all__
            assert hasattr(scrapebadger, name)
