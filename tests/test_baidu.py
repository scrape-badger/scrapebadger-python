"""Unit tests for the Baidu SDK client — endpoint routing and full field coverage.

The SDK drops any field the model does not declare, so the parsing tests assert
every field in the API contract survives ``model_validate``.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from scrapebadger.baidu.client import BaiduClient
from scrapebadger.baidu.models import (
    AutocompleteResponse,
    ImagesResponse,
    NewsResponse,
    SearchResponse,
)

ORGANIC_RESULT: dict[str, Any] = {
    "position": 1,
    "title": "专业咖啡机价格 - 阿里巴巴",
    "url": "https://www.1688.com/jiage/-D7A8D2B5BFA7B7C8BBFA.html",
    "baidu_url": "http://www.baidu.com/link?url=m4_ZyR-m51ZWH",
    "display_url": "www.1688.com",
    "snippet": "阿里巴巴为您找到2,955个今日最新的专业咖啡机价格",
    "source": "阿里巴巴1688",
    "date": "2026年7月27日",
    "date_at": "2026-07-27",
    "thumbnail": "https://t9.baidu.com/it/u=1053246899,2367519289",
    "tpl": "www_index",
}
SEARCH_RESPONSE: dict[str, Any] = {
    "query": "咖啡机",
    "page": 1,
    "num": 10,
    "total_results": 4_820_000,
    "results": [ORGANIC_RESULT],
    "related_searches": [{"query": "咖啡机厂家", "url": "https://www.baidu.com/s?wd=%E5%92%96"}],
    "url": "https://www.baidu.com/s?wd=%E5%92%96%E5%95%A1%E6%9C%BA&ie=utf-8",
}
NEWS_RESULT: dict[str, Any] = {
    "position": 1,
    "title": "以科学了解咖啡的秘密",
    "url": "http://www.jgj.moa.gov.cn/kptd/202012/t20201207_6357680.htm",
    "baidu_url": "http://www.baidu.com/link?url=abc",
    "snippet": "咖啡是用经过烘焙的咖啡豆制作冲泡的饮料",
    "source": "农产品质量安全监管司",
    "date": "2020年12月25日",
    "date_at": "2020-12-25",
    "thumbnail": "https://t9.baidu.com/it/u=546988488,560360434",
}
NEWS_RESPONSE: dict[str, Any] = {
    "query": "人工智能",
    "page": 1,
    "total_results": 12_300,
    "results": [NEWS_RESULT],
    "url": "https://www.baidu.com/s?tn=news&word=%E4%BA%BA&ie=utf-8",
}
IMAGE_RESULT: dict[str, Any] = {
    "position": 1,
    "title": "白杯,咖啡,咖啡豆 4k",
    "image_url": "https://s2.best-wallpaper.net/wallpaper/iphone/1708/White-cup.jpg",
    "thumbnail_url": "https://img0.baidu.com/it/u=1467163901,1497482106?w=282&h=500",
    "middle_url": "https://img0.baidu.com/it/u=1467163901,1497482106?w=282&h=500",
    "hover_url": "https://img0.baidu.com/it/u=1467163901,1497482106?w=282&h=500",
    "width": 640,
    "height": 1136,
    "type": "jpg",
    "from_url": "http://cn.best-wallpaper.net/white-cup-coffee-coffee-beans.html",
    "from_title": "白杯,咖啡,咖啡豆 4k",
}
IMAGES_RESPONSE: dict[str, Any] = {
    "query": "猫",
    "page": 1,
    "total_results": 748_836,
    "results": [IMAGE_RESULT],
}
AUTOCOMPLETE_RESPONSE: dict[str, Any] = {
    "query": "咖啡",
    "suggestions": [
        {"query": "咖啡品牌排行榜", "type": "sug"},
        {"query": "咖啡机", "type": "sug"},
    ],
}


@pytest.fixture
def mock_base_client() -> MagicMock:
    client = MagicMock()
    client.get = AsyncMock()
    return client


@pytest.fixture
def baidu(mock_base_client: MagicMock) -> BaiduClient:
    return BaiduClient(mock_base_client)


# =============================================================================
# Routing
# =============================================================================


@pytest.mark.asyncio
async def test_search_routes_and_defaults(baidu: BaiduClient, mock_base_client: MagicMock) -> None:
    mock_base_client.get.return_value = SEARCH_RESPONSE

    await baidu.search("咖啡机")

    mock_base_client.get.assert_awaited_once_with(
        "/v1/baidu/search",
        params={
            "query": "咖啡机",
            "page": 1,
            "num": 10,
            "language": "all",
            "time_from": None,
            "time_to": None,
        },
    )


@pytest.mark.asyncio
async def test_search_forwards_all_filters(baidu: BaiduClient, mock_base_client: MagicMock) -> None:
    mock_base_client.get.return_value = SEARCH_RESPONSE

    await baidu.search(
        "咖啡机",
        page=3,
        num=50,
        language="zh-tw",
        time_from=1_754_000_000,
        time_to=1_754_400_000,
    )

    assert mock_base_client.get.await_args.kwargs["params"] == {
        "query": "咖啡机",
        "page": 3,
        "num": 50,
        "language": "zh-tw",
        "time_from": 1_754_000_000,
        "time_to": 1_754_400_000,
    }


@pytest.mark.asyncio
async def test_news_routes(baidu: BaiduClient, mock_base_client: MagicMock) -> None:
    mock_base_client.get.return_value = NEWS_RESPONSE

    await baidu.news("人工智能", page=2, sort="time")

    mock_base_client.get.assert_awaited_once_with(
        "/v1/baidu/news", params={"query": "人工智能", "page": 2, "sort": "time"}
    )


@pytest.mark.asyncio
async def test_images_routes(baidu: BaiduClient, mock_base_client: MagicMock) -> None:
    mock_base_client.get.return_value = IMAGES_RESPONSE

    await baidu.images("猫")

    mock_base_client.get.assert_awaited_once_with(
        "/v1/baidu/images", params={"query": "猫", "page": 1}
    )


@pytest.mark.asyncio
async def test_autocomplete_routes(baidu: BaiduClient, mock_base_client: MagicMock) -> None:
    mock_base_client.get.return_value = AUTOCOMPLETE_RESPONSE

    result = await baidu.autocomplete("咖啡")

    mock_base_client.get.assert_awaited_once_with(
        "/v1/baidu/autocomplete", params={"query": "咖啡"}
    )
    assert isinstance(result, AutocompleteResponse)
    assert [s.query for s in result.suggestions] == ["咖啡品牌排行榜", "咖啡机"]
    assert result.suggestions[0].type == "sug"


# =============================================================================
# Field coverage — nothing in the contract may be silently dropped
# =============================================================================


def test_search_response_keeps_every_field() -> None:
    parsed = SearchResponse.model_validate(SEARCH_RESPONSE)

    assert parsed.model_dump(exclude={"results", "related_searches"}) == {
        k: v for k, v in SEARCH_RESPONSE.items() if k not in {"results", "related_searches"}
    }
    assert parsed.results[0].model_dump() == ORGANIC_RESULT
    assert parsed.related_searches[0].query == "咖啡机厂家"


def test_news_response_keeps_every_field() -> None:
    parsed = NewsResponse.model_validate(NEWS_RESPONSE)

    assert parsed.model_dump(exclude={"results"}) == {
        k: v for k, v in NEWS_RESPONSE.items() if k != "results"
    }
    assert parsed.results[0].model_dump() == NEWS_RESULT


def test_images_response_keeps_every_field() -> None:
    parsed = ImagesResponse.model_validate(IMAGES_RESPONSE)

    assert parsed.model_dump(exclude={"results"}) == {
        k: v for k, v in IMAGES_RESPONSE.items() if k != "results"
    }
    assert parsed.results[0].model_dump() == IMAGE_RESULT


def test_real_url_and_tracking_url_are_separate() -> None:
    """The USP: `url` is the real destination, `baidu_url` the redirect."""
    result = SearchResponse.model_validate(SEARCH_RESPONSE).results[0]

    assert result.url is not None and "baidu.com" not in result.url
    assert result.baidu_url is not None and result.baidu_url.startswith(
        "http://www.baidu.com/link?url="
    )


def test_nullable_fields_default_to_none() -> None:
    """Only position/title/query/page/num are required — the rest may be absent."""
    parsed = SearchResponse.model_validate(
        {"query": "q", "page": 1, "num": 10, "url": "u", "results": [{"position": 1, "title": "t"}]}
    )

    assert parsed.total_results is None
    assert parsed.related_searches == []
    assert parsed.results[0].url is None
    assert parsed.results[0].date_at is None
