"""Unit tests for the Naver SDK client — endpoint routing and field coverage.

The SDK drops any field the model does not declare, so the parsing tests
assert the documented fields survive ``model_validate``.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from scrapebadger.naver.client import NaverClient
from scrapebadger.naver.models import (
    PlaceDetailResponse,
    PriceCompareResponse,
    SearchResponse,
    ShoppingBestsellersResponse,
    StoreProfileResponse,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_base_client() -> MagicMock:
    client = MagicMock()
    client.get = AsyncMock(return_value={})
    return client


@pytest.fixture
def naver(mock_base_client: MagicMock) -> NaverClient:
    return NaverClient(mock_base_client)


# =============================================================================
# Search vertical routing
# =============================================================================


@pytest.mark.asyncio
async def test_search_routes_and_defaults(naver: NaverClient, mock_base_client: MagicMock) -> None:
    await naver.search.search("커피머신")
    mock_base_client.get.assert_awaited_once_with(
        "/v1/naver/search",
        params={"query": "커피머신", "page": 1, "view": None},
    )


@pytest.mark.asyncio
async def test_search_forwards_view_and_page(
    naver: NaverClient, mock_base_client: MagicMock
) -> None:
    await naver.search.search("커피", page=3, view="more")
    assert mock_base_client.get.await_args.kwargs["params"] == {
        "query": "커피",
        "page": 3,
        "view": "more",
    }


@pytest.mark.asyncio
async def test_news_defaults(naver: NaverClient, mock_base_client: MagicMock) -> None:
    await naver.search.news("ai")
    mock_base_client.get.assert_awaited_once_with(
        "/v1/naver/news",
        params={"query": "ai", "page": 1, "sort": "relevance"},
    )


@pytest.mark.asyncio
async def test_autocomplete_routes(naver: NaverClient, mock_base_client: MagicMock) -> None:
    await naver.search.autocomplete("커")
    mock_base_client.get.assert_awaited_once_with("/v1/naver/autocomplete", params={"query": "커"})


@pytest.mark.asyncio
async def test_local_forwards_geo(naver: NaverClient, mock_base_client: MagicMock) -> None:
    await naver.search.local("강남 카페", start=11, display=20, x=127.0, y=37.5)
    assert mock_base_client.get.await_args.kwargs["params"] == {
        "query": "강남 카페",
        "start": 11,
        "display": 20,
        "x": 127.0,
        "y": 37.5,
    }


@pytest.mark.asyncio
async def test_web_vertical_path(naver: NaverClient, mock_base_client: MagicMock) -> None:
    await naver.search.web("query", page=2)
    mock_base_client.get.assert_awaited_once_with(
        "/v1/naver/search/web", params={"query": "query", "page": 2}
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("vertical", ["blog", "cafe", "kin", "image", "video", "clip"])
async def test_simple_verticals_route(
    naver: NaverClient, mock_base_client: MagicMock, vertical: str
) -> None:
    await getattr(naver.search, vertical)("q")
    mock_base_client.get.assert_awaited_once_with(
        f"/v1/naver/{vertical}", params={"query": "q", "page": 1}
    )


# =============================================================================
# Place routing
# =============================================================================


@pytest.mark.asyncio
async def test_place_get_path(naver: NaverClient, mock_base_client: MagicMock) -> None:
    await naver.places.get("1234567890")
    mock_base_client.get.assert_awaited_once_with("/v1/naver/place/1234567890")


@pytest.mark.asyncio
async def test_place_reviews_defaults(naver: NaverClient, mock_base_client: MagicMock) -> None:
    await naver.places.reviews("1234567890")
    mock_base_client.get.assert_awaited_once_with(
        "/v1/naver/place/1234567890/reviews", params={"cursor": None, "size": 20}
    )


@pytest.mark.asyncio
async def test_place_photos_defaults(naver: NaverClient, mock_base_client: MagicMock) -> None:
    await naver.places.photos("1234567890")
    mock_base_client.get.assert_awaited_once_with(
        "/v1/naver/place/1234567890/photos",
        params={"media_source": "placeReview", "cursor": None},
    )


# =============================================================================
# Shopping routing
# =============================================================================


@pytest.mark.asyncio
async def test_shopping_bestsellers_defaults(
    naver: NaverClient, mock_base_client: MagicMock
) -> None:
    await naver.shopping.bestsellers()
    mock_base_client.get.assert_awaited_once_with(
        "/v1/naver/shopping/bestsellers",
        params={
            "category_id": "ALL",
            "age_type": "ALL",
            "sort_type": "PRODUCT_CLICK",
            "period_type": "DAILY",
        },
    )


@pytest.mark.asyncio
async def test_shopping_insight_required_args(
    naver: NaverClient, mock_base_client: MagicMock
) -> None:
    await naver.shopping.insight("50000000", "2026-01-01", "2026-01-31")
    assert mock_base_client.get.await_args.kwargs["params"] == {
        "category_id": "50000000",
        "start_date": "2026-01-01",
        "end_date": "2026-01-31",
        "time_unit": "date",
        "age": "",
        "gender": "",
        "device": "",
        "count": 20,
    }


@pytest.mark.asyncio
async def test_shopping_vertical_path(naver: NaverClient, mock_base_client: MagicMock) -> None:
    await naver.shopping.vertical("fashiontown")
    mock_base_client.get.assert_awaited_once_with("/v1/naver/shopping/verticals/fashiontown")


@pytest.mark.asyncio
async def test_shopping_categories_no_params(
    naver: NaverClient, mock_base_client: MagicMock
) -> None:
    await naver.shopping.categories()
    mock_base_client.get.assert_awaited_once_with("/v1/naver/shopping/categories")


@pytest.mark.asyncio
async def test_shopping_search_catalog_defaults(
    naver: NaverClient, mock_base_client: MagicMock
) -> None:
    await naver.shopping.search_catalog("아이폰")
    mock_base_client.get.assert_awaited_once_with(
        "/v1/naver/shopping/search-catalog",
        params={"query": "아이폰", "sort": "RECOMMEND", "page": 1},
    )


# =============================================================================
# Shopping Live routing (nested sub-client)
# =============================================================================


@pytest.mark.asyncio
async def test_live_broadcast_path(naver: NaverClient, mock_base_client: MagicMock) -> None:
    await naver.shopping.live.broadcast("abc123")
    mock_base_client.get.assert_awaited_once_with("/v1/naver/shopping/live/broadcasts/abc123")


@pytest.mark.asyncio
async def test_live_channel_products_cursor(
    naver: NaverClient, mock_base_client: MagicMock
) -> None:
    await naver.shopping.live.channel_products("chan", next="99", size=50)
    mock_base_client.get.assert_awaited_once_with(
        "/v1/naver/shopping/live/channels/chan/products",
        params={"next": "99", "size": 50},
    )


@pytest.mark.asyncio
async def test_live_replay_products_defaults(
    naver: NaverClient, mock_base_client: MagicMock
) -> None:
    await naver.shopping.live.replay_products("bc1")
    mock_base_client.get.assert_awaited_once_with(
        "/v1/naver/shopping/live/broadcasts/bc1/replay-products",
        params={"include_before": True, "next": "0"},
    )


@pytest.mark.asyncio
async def test_live_search_keywords_no_params(
    naver: NaverClient, mock_base_client: MagicMock
) -> None:
    await naver.shopping.live.search_keywords()
    mock_base_client.get.assert_awaited_once_with("/v1/naver/shopping/live/search/keywords")


# =============================================================================
# Stores routing
# =============================================================================


@pytest.mark.asyncio
async def test_store_profile_defaults(naver: NaverClient, mock_base_client: MagicMock) -> None:
    await naver.stores.get("somestore")
    mock_base_client.get.assert_awaited_once_with(
        "/v1/naver/stores/somestore", params={"host": "smartstore"}
    )


@pytest.mark.asyncio
async def test_store_products_forwards_all(naver: NaverClient, mock_base_client: MagicMock) -> None:
    await naver.stores.products(
        "somestore",
        host="brand",
        category_id="c1",
        page=2,
        size=40,
        sort="RECENT",
        channel_uid="u1",
    )
    assert mock_base_client.get.await_args.args[0] == "/v1/naver/stores/somestore/products"
    assert mock_base_client.get.await_args.kwargs["params"] == {
        "host": "brand",
        "category_id": "c1",
        "page": 2,
        "size": 40,
        "sort": "RECENT",
        "channel_uid": "u1",
    }


# =============================================================================
# Products + reviews routing
# =============================================================================


@pytest.mark.asyncio
async def test_product_detail_defaults(naver: NaverClient, mock_base_client: MagicMock) -> None:
    await naver.products.get("987")
    mock_base_client.get.assert_awaited_once_with(
        "/v1/naver/products/987",
        params={
            "host": "brand",
            "store_url": None,
            "channel_uid": None,
            "broadcast_id": None,
            "live_channel_id": None,
            "query": None,
        },
    )


@pytest.mark.asyncio
async def test_product_reviews_required_kwargs(
    naver: NaverClient, mock_base_client: MagicMock
) -> None:
    await naver.products.reviews("111", store_url="somestore", product_no="222")
    assert mock_base_client.get.await_args.args[0] == "/v1/naver/products/111/reviews"
    assert mock_base_client.get.await_args.kwargs["params"] == {
        "store_url": "somestore",
        "product_no": "222",
        "host": "smartstore",
        "channel_uid": None,
        "checkout_merchant_no": None,
        "page": 1,
        "sort": "REVIEW_RANKING",
    }


@pytest.mark.asyncio
async def test_group_review_summary_path(naver: NaverClient, mock_base_client: MagicMock) -> None:
    await naver.products.group_review_summary("g1", leaf_category_id="leaf")
    mock_base_client.get.assert_awaited_once_with(
        "/v1/naver/product-groups/g1/review-summary", params={"leaf_category_id": "leaf"}
    )


@pytest.mark.asyncio
async def test_review_video_inkey_routes(naver: NaverClient, mock_base_client: MagicMock) -> None:
    await naver.reviews.video_inkey(attach_vid="v", stamp="s")
    mock_base_client.get.assert_awaited_once_with(
        "/v1/naver/reviews/video-inkey", params={"attach_vid": "v", "stamp": "s"}
    )


@pytest.mark.asyncio
async def test_review_detail_path(naver: NaverClient, mock_base_client: MagicMock) -> None:
    await naver.reviews.get("r1")
    mock_base_client.get.assert_awaited_once_with("/v1/naver/reviews/r1")


# =============================================================================
# Parsing / field coverage
# =============================================================================


def test_search_response_parses_full_payload() -> None:
    payload: dict[str, Any] = {
        "query": "커피",
        "page": 1,
        "result_count": 2,
        "results": [
            {
                "position": 1,
                "title": "T",
                "url": "https://example.com",
                "display_url": "example.com",
                "snippet": "S",
                "source": "src",
            }
        ],
        "related_searches": [{"query": "커피머신", "url": "https://naver.com/s"}],
        "place_results": [{"place_id": "1", "name": "cafe"}],
        "url": "https://search.naver.com/search.naver",
    }
    parsed = SearchResponse.model_validate(payload)
    assert parsed.result_count == 2
    assert parsed.results[0].title == "T"
    assert parsed.related_searches[0].query == "커피머신"
    assert parsed.place_results[0]["name"] == "cafe"


def test_shopping_bestsellers_parses_products() -> None:
    payload: dict[str, Any] = {
        "category_id": "ALL",
        "age_type": "ALL",
        "sort_type": "PRODUCT_CLICK",
        "period_type": "DAILY",
        "sync_date": "2026-01-01",
        "result_count": 1,
        "products": [
            {
                "rank": 1,
                "nv_mid": "m1",
                "title": "노트북",
                "price": 1000000,
                "discount_price": 900000,
                "discount_rate": 10,
                "review_score": 4.5,
                "review_count": 123,
                "mall_name": "mall",
                "is_ad": False,
            }
        ],
    }
    parsed = ShoppingBestsellersResponse.model_validate(payload)
    assert parsed.products[0].rank == 1
    assert parsed.products[0].review_score == 4.5
    assert parsed.products[0].is_ad is False


def test_place_detail_parses_menus() -> None:
    payload: dict[str, Any] = {
        "place_id": "1",
        "name": "cafe",
        "category": "카페",
        "rating": 4.2,
        "menus": [{"name": "아메리카노", "price": "4,500원"}],
        "images": ["https://img"],
        "latitude": 37.5,
        "longitude": 127.0,
        "source_url": "https://m.place.naver.com",
    }
    parsed = PlaceDetailResponse.model_validate(payload)
    assert parsed.menus[0].price == "4,500원"
    assert parsed.latitude == 37.5


def test_store_profile_masks_identity_fields() -> None:
    parsed = StoreProfileResponse.model_validate(
        {"store_url": "s", "host": "smartstore", "follower_count": 10, "phone": "secret"}
    )
    assert parsed.follower_count == 10
    # Unknown/masked fields are dropped (extra="ignore").
    assert not hasattr(parsed, "phone")


def test_price_compare_parses_offers() -> None:
    parsed = PriceCompareResponse.model_validate(
        {
            "query": "아이폰",
            "entries": [
                {
                    "catalog_id": "c1",
                    "offer_count": 2,
                    "best_price": 900000,
                    "offers": [{"mall_name": "m", "price": 900000, "naver_pay": True}],
                }
            ],
            "offers": [{"mall_name": "m2", "price": 950000}],
            "offers_note": "note",
        }
    )
    assert parsed.entries[0].offers[0].naver_pay is True
    assert parsed.offers[0].price == 950000
