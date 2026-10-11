"""Unit tests for Facebook SDK methods."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from scrapebadger.facebook.client import FacebookClient


@pytest.fixture
def mock_base_client() -> MagicMock:
    client = MagicMock()
    client.get = AsyncMock(return_value={"posts": [], "count": 0})
    return client


@pytest.fixture
def facebook_client(mock_base_client: MagicMock) -> FacebookClient:
    return FacebookClient(mock_base_client)


class TestGroupPosts:
    async def test_group_posts_leave_the_newest_first_default_to_the_api(
        self, facebook_client: FacebookClient, mock_base_client: MagicMock
    ) -> None:
        await facebook_client.get_group_posts("rentasenplayadelcarmen")
        args, kwargs = mock_base_client.get.call_args
        assert args[0] == "/v1/facebook/groups/rentasenplayadelcarmen/posts"
        assert kwargs["params"] == {}

    async def test_group_posts_pass_sort_and_cursor(
        self, facebook_client: FacebookClient, mock_base_client: MagicMock
    ) -> None:
        await facebook_client.get_group_posts("123", after="CUR", sort="relevance")
        assert mock_base_client.get.call_args[1]["params"] == {
            "after": "CUR",
            "sort": "relevance",
        }
