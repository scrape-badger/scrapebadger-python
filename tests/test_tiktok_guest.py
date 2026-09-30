from unittest.mock import AsyncMock, MagicMock

import pytest

from scrapebadger.tiktok.trending import TrendingClient
from scrapebadger.tiktok.users import UsersClient


@pytest.mark.parametrize(
    "method,key,suffix",
    [
        ("get_followers", "users", "followers"),
        ("get_following", "users", "following"),
        ("get_liked", "videos", "liked"),
        ("get_reposts", "videos", "reposts"),
    ],
)
async def test_guest_cursor_forwarded(method, key, suffix):
    base = MagicMock()
    base.get = AsyncMock(
        return_value={key: [], "pagination": {"has_more": False, "count": 0}, "region": "US"}
    )
    await getattr(UsersClient(base), method)("tiktok", cursor="tw1_test")
    assert base.get.call_args.args[0] == "/v1/tiktok/users/tiktok/" + suffix
    assert base.get.call_args.kwargs["params"]["cursor"] == "tw1_test"


async def test_trends_no_default_period():
    base = MagicMock()
    base.get = AsyncMock(return_value={"songs": [], "region": "US"})
    await TrendingClient(base).songs()
    assert "period" not in base.get.call_args.kwargs["params"]
