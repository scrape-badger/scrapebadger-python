from unittest.mock import AsyncMock

import pytest

from scrapebadger.google.search import SearchClient


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "method,path", [("search", "/v1/google/search"), ("light", "/v1/google/light/search")]
)
async def test_deferred_links_is_opt_in_and_forwarded(method, path):
    base = AsyncMock()
    client = SearchClient(base)
    await getattr(client, method)("cats")
    assert "defer_links" not in base.get.call_args.kwargs["params"]
    await getattr(client, method)("cats", defer_links=True)
    assert base.get.call_args.args[0] == path
    assert base.get.call_args.kwargs["params"]["defer_links"] is True
