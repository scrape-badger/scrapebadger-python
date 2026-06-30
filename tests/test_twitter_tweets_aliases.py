"""SCR-52: advanced_search/_all aliases on TweetsClient.

Customers reached for ``client.twitter.tweets.advanced_search(...)`` (the REST
endpoint name) and hit ``AttributeError``. These thin aliases delegate to
``search`` / ``search_all`` so the endpoint-named call works.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock

import pytest

from scrapebadger._internal.client import BaseClient
from scrapebadger._internal.config import ClientConfig
from scrapebadger.twitter.tweets import TweetsClient


@pytest.fixture
def tweets_client() -> TweetsClient:
    return TweetsClient(BaseClient(ClientConfig(api_key="test_key", max_retries=1)))


async def test_advanced_search_delegates_to_search(tweets_client: TweetsClient) -> None:
    page: dict[str, Any] = {"data": [{"id": "1"}], "next_cursor": None}
    tweets_client._client.get = AsyncMock(return_value=page)  # type: ignore[method-assign]

    result = await tweets_client.advanced_search("python")

    assert [t.id for t in result.data] == ["1"]
    assert tweets_client._client.get.call_args[0][0] == "/v1/twitter/tweets/advanced_search"


async def test_advanced_search_all_delegates_to_search_all(
    tweets_client: TweetsClient,
) -> None:
    page: dict[str, Any] = {"data": [{"id": "1"}, {"id": "2"}]}
    headers: dict[str, str] = {}
    tweets_client._client.get_with_headers = AsyncMock(return_value=(page, headers))  # type: ignore[method-assign]

    ids = [t.id async for t in tweets_client.advanced_search_all("python")]

    assert ids == ["1", "2"]
    assert tweets_client._client.get_with_headers.call_args[0][0] == (
        "/v1/twitter/tweets/advanced_search"
    )
