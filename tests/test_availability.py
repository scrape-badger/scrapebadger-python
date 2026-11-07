from unittest.mock import AsyncMock

import pytest

from scrapebadger import ScrapeBadger


@pytest.mark.asyncio
async def test_live_catalog_refreshes_after_admin_change():
    async with ScrapeBadger(api_key="test") as client:
        row = {
            "method": "GET",
            "path": "/v1/example/search",
            "api": "example",
            "status": "deprecated",
        }
        mock = AsyncMock(side_effect=[{"endpoints": [row]}, {"endpoints": []}])
        client._base_client.get = mock
        assert await client.endpoints() == [row]
        assert await client.endpoints() == []
        assert mock.call_count == 2
        mock.assert_called_with("/api/public/endpoint-catalog")
